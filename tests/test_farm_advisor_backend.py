import unittest

from farm_advisor_backend import FarmAdvisorAPI, GeminiAdvisor, SensorData


class FarmAdvisorBackendTests(unittest.TestCase):
    def setUp(self):
        self.api = FarmAdvisorAPI()

    def test_sensor_condition_thresholds(self):
        critical = {"distance_cm": 12, "temperature_c": 25}
        warning = {"distance_cm": 25, "temperature_c": 25}
        normal = {"distance_cm": 55, "temperature_c": 25}

        self.assertIn("CRITICAL", SensorData.assess_conditions(critical)[0])
        self.assertIn("WARNING", SensorData.assess_conditions(warning)[0])
        self.assertIn("NORMAL", SensorData.assess_conditions(normal)[0])

    def test_runoff_risk_high_with_ponding_and_rain(self):
        forecast = [
            {"probabilityOfPrecipitation": {"value": 80}},
            {"probabilityOfPrecipitation": {"value": 70}},
            {"probabilityOfPrecipitation": {"value": 0}},
        ]
        sensor = {
            "distance_cm": 10,
            "temperature_c": 12,
            "ponding_detected": True,
        }

        risk = self.api.calculate_runoff_risk(forecast, sensor)

        self.assertEqual(risk["level"], "HIGH")
        self.assertEqual(risk["indicator"], "red")
        self.assertGreaterEqual(risk["score"], 5)

    def test_runoff_risk_low_for_dry_field(self):
        forecast = [{"probabilityOfPrecipitation": {"value": 10}}]
        sensor = {
            "distance_cm": 65,
            "temperature_c": 22,
            "ponding_detected": False,
        }

        risk = self.api.calculate_runoff_risk(forecast, sensor)

        self.assertEqual(risk["level"], "LOW")
        self.assertEqual(risk["score"], 0)

    def test_ai_advisor_without_key_is_graceful(self):
        advisor = GeminiAdvisor(api_key="")
        sensor = {
            "distance_cm": 65,
            "temperature_c": 22,
            "ponding_detected": False,
        }

        advice = advisor.get_advice([], sensor, "Should I irrigate?")

        self.assertIn("GEMINI_API_KEY", advice)


if __name__ == "__main__":
    unittest.main()
