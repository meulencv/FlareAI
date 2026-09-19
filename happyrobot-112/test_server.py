import unittest

from server import parse_summary


class ParseSummaryTests(unittest.TestCase):
    def test_extracts_latest_complete_ficha(self):
        messages = [
            {
                "content": (
                    "Ficha: Ubicación: Calle Mayor 4, Madrid | Emergencia: incendio en cocina | "
                    "Personas: dos, fuera de la vivienda | Riesgos: humo | Contacto: 600 123 123"
                )
            }
        ]

        self.assertEqual(
            parse_summary(messages),
            {
                "ubicacion": "Calle Mayor 4, Madrid",
                "emergencia": "incendio en cocina",
                "personas": "dos, fuera de la vivienda",
                "riesgos": "humo",
                "contacto": "600 123 123",
            },
        )

    def test_uses_last_ficha_after_a_correction(self):
        messages = [
            {
                "content": (
                    "Ficha: Ubicación: Calle Mayor 4 | Emergencia: fuego | "
                    "Personas: pendiente | Riesgos: pendiente | Contacto: pendiente"
                )
            },
            {"content": "El llamante corrige el número."},
            {
                "content": (
                    "Entendido. Ficha: Ubicación: Calle Mayor 14 | Emergencia: fuego | "
                    "Personas: una | Riesgos: humo | Contacto: pendiente"
                )
            },
        ]

        self.assertEqual(parse_summary(messages)["ubicacion"], "Calle Mayor 14")

    def test_merges_interrupted_fichas(self):
        messages = [
            {
                "content": (
                    "Ficha: Emergencia: incendio | Ubicación: calle Mayor 4 | "
                    "Personas: pendiente | Riesgos: pendiente | Contacto: pendiente"
                )
            },
            {"content": "Ficha: Emergencia: incendio | Ubicación: calle Mayor 14"},
        ]

        self.assertEqual(
            parse_summary(messages),
            {
                "ubicacion": "calle Mayor 14",
                "emergencia": "incendio",
                "personas": "pendiente",
                "riesgos": "pendiente",
                "contacto": "pendiente",
            },
        )

    def test_accepts_unaccented_location_label(self):
        messages = [
            {
                "content": (
                    "Ficha: Ubicacion: AP-7 km 120 | Emergencia: accidente | "
                    "Personas: tres | Riesgos: tráfico | Contacto: 611 111 111."
                )
            }
        ]

        self.assertEqual(parse_summary(messages)["ubicacion"], "AP-7 km 120")
        self.assertEqual(parse_summary(messages)["contacto"], "611 111 111")

    def test_infers_urgent_fallback_from_caller_transcript(self):
        messages = [
            {"role": "user", "content": "Hay fuego, no podemos salir."},
            {"role": "user", "content": "Estamos atrapados y hay mucho humo."},
            {"role": "assistant", "content": "Ficha:"},
        ]

        summary = parse_summary(messages)

        self.assertEqual(summary["emergencia"], "Incendio / fuego")
        self.assertIn("personas atrapadas", summary["riesgos"])

    def test_uses_silent_tool_calls_and_applies_corrections(self):
        messages = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "actualizar_ficha",
                            "arguments": (
                                '{"ubicacion":"Calle Rosetas 18, Barcelona",'
                                '"emergencia":"Incendio en vivienda"}'
                            ),
                        }
                    }
                ],
            },
            {
                "role": "assistant",
                "tool_calls": {
                    "name": "actualizar_ficha",
                    "arguments": {
                        "ubicacion": "Calle Rosetas 28, Barcelona",
                        "personas": "34 personas atrapadas",
                        "riesgos": "Humo intenso",
                    },
                },
            },
        ]

        summary = parse_summary(messages)

        self.assertEqual(summary["ubicacion"], "Calle Rosetas 28, Barcelona")
        self.assertEqual(summary["emergencia"], "Incendio en vivienda")
        self.assertEqual(summary["personas"], "34 personas atrapadas")
        self.assertEqual(summary["riesgos"], "Humo intenso")


if __name__ == "__main__":
    unittest.main()
