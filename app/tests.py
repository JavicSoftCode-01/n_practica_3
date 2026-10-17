import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, Client
from fastapi.testclient import TestClient

from app.api import api_app
from app.models import Persona


class PersonaAPITestCase(TestCase):
    """
    Suite de pruebas automatizadas para la API FastAPI,
    los modelos Django y las restricciones nativas en PostgreSQL.
    """

    def setUp(self):
        self.fastapi_client = TestClient(api_app)
        self.django_client = Client()

    def test_01_creacion_persona_valida_post_y_get(self):
        """
        Verifica que POST /api/personas con datos válidos retorna 201 Created
        y que posteriormente GET /api/personas lista el registro.
        """
        payload = {
            "nombres_completos": "Juan Carlos Perez Gomez",
            "fecha_nacimiento": "1995-05-15",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertEqual(data["nombres_completos"], "Juan Carlos Perez Gomez")
        self.assertEqual(data["fecha_nacimiento"], "1995-05-15")
        self.assertIn("id", data)

        # Verificar consulta GET
        get_res = self.fastapi_client.get("/api/personas")
        self.assertEqual(get_res.status_code, 200)
        items = get_res.json()
        self.assertTrue(len(items) >= 1)
        self.assertEqual(items[0]["nombres_completos"], "Juan Carlos Perez Gomez")

    def test_02_rechazo_nombres_una_sola_palabra(self):
        """Rechaza nombres_completos con 1 palabra (mínimo 2 requeridas)."""
        payload = {
            "nombres_completos": "Juan",
            "fecha_nacimiento": "1990-01-01",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_03_rechazo_nombres_cinco_palabras(self):
        """Rechaza nombres_completos con 5 palabras (máximo 4 permitidas)."""
        payload = {
            "nombres_completos": "Juan Carlos Alberto Perez Gomez",
            "fecha_nacimiento": "1990-01-01",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_04_rechazo_nombres_con_numeros_o_simbolos(self):
        """Rechaza nombres_completos con caracteres no alfabéticos."""
        payload1 = {
            "nombres_completos": "Juan Perez 123",
            "fecha_nacimiento": "1990-01-01",
        }
        response1 = self.fastapi_client.post("/api/personas", json=payload1)
        self.assertEqual(response1.status_code, 422)

        payload2 = {
            "nombres_completos": "Ana@Maria Lopez",
            "fecha_nacimiento": "1990-01-01",
        }
        response2 = self.fastapi_client.post("/api/personas", json=payload2)
        self.assertEqual(response2.status_code, 422)

    def test_05_rechazo_nombres_longitud_mayor_a_60(self):
        """Rechaza nombres_completos que superen los 60 caracteres."""
        payload = {
            "nombres_completos": "NombreExtremadamenteLargoConMuchosCaracteresParaQueSuperelosSesenta CaracteresTotales",
            "fecha_nacimiento": "1990-01-01",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_06_rechazo_fecha_menor_a_1970(self):
        """Rechaza fechas de nacimiento anteriores al 01/01/1970."""
        payload = {
            "nombres_completos": "Carlos Gomez",
            "fecha_nacimiento": "1969-12-31",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_07_rechazo_fecha_mayor_a_2100(self):
        """Rechaza fechas de nacimiento posteriores al 31/12/2100."""
        payload = {
            "nombres_completos": "Carlos Gomez",
            "fecha_nacimiento": "2101-01-01",
        }
        response = self.fastapi_client.post("/api/personas", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_08_metodos_http_no_permitidos_retornan_405(self):
        """
        Verifica que PUT, DELETE y PATCH sobre /api/personas retornan 405 Method Not Allowed.
        """
        for method in ['put', 'delete', 'patch']:
            client_method = getattr(self.fastapi_client, method)
            res = client_method("/api/personas")
            self.assertEqual(
                res.status_code,
                405,
                f"El método {method.upper()} no retornó 405 (retornó {res.status_code})"
            )

    def test_09_vista_principal_django_index(self):
        """
        Verifica que GET / responde 200 OK y contiene la estructura del layout 20% y 70%.
        """
        response = self.django_client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("panel-form", content)
        self.assertIn("panel-table", content)
        self.assertIn("20%", content)
        self.assertIn("70%", content)
        self.assertIn("nombres_completos", content)
        self.assertIn("fecha_nacimiento", content)

    def test_10_modelo_django_validaciones_directas(self):
        """
        Verifica que Persona.full_clean() del modelo Django rechaza datos inválidos.
        """
        # 1 palabra
        p1 = Persona(nombres_completos="Juan", fecha_nacimiento=datetime.date(1990, 1, 1))
        with self.assertRaises(ValidationError):
            p1.full_clean()

        # 5 palabras
        p2 = Persona(
            nombres_completos="Uno Dos Tres Cuatro Cinco",
            fecha_nacimiento=datetime.date(1990, 1, 1),
        )
        with self.assertRaises(ValidationError):
            p2.full_clean()

        # Fecha fuera de rango
        p3 = Persona(
            nombres_completos="Juan Perez",
            fecha_nacimiento=datetime.date(1960, 5, 10),
        )
        with self.assertRaises(ValidationError):
            p3.full_clean()
