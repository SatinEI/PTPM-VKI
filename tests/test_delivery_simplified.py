import unittest

from src.delivery_service  import calculate_delivery_cost


INVALID = (-1, "0000-00-00")


class TestDeliveryCost(unittest.TestCase):
    def test_invalid_weight_limits(self):
        self.assertEqual(calculate_delivery_cost(0.099, 100, "обычный"), INVALID)
        self.assertEqual(calculate_delivery_cost(50.001, 100, "обычный"), INVALID)

    def test_invalid_distance_limits(self):
        self.assertEqual(calculate_delivery_cost(1, 0, "обычный"), INVALID)
        self.assertEqual(calculate_delivery_cost(1, 5001, "обычный"), INVALID)

    def test_minimum_and_maximum_limits_are_valid(self):
        self.assertEqual(
            calculate_delivery_cost(0.1, 1, "обычный"),
            (205, "2026-10-04"),
        )
        self.assertEqual(
            calculate_delivery_cost(50, 5000, "обычный"),
            (37800, "2026-10-13"),
        )

    def test_invalid_package_type(self):
        result = calculate_delivery_cost(1, 100, "другой")
        self.assertEqual(result, INVALID)

    def test_weight_tariff(self):
        self.assertEqual(calculate_delivery_cost(5, 100, "обычный")[0], 700)
        self.assertEqual(calculate_delivery_cost(5.001, 100, "обычный")[0], 840)
        self.assertEqual(calculate_delivery_cost(20, 100, "обычный")[0], 1050)

    def test_packages(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный")[0], 700)
        self.assertEqual(calculate_delivery_cost(1, 100, "хрупкий")[0], 1000)
        self.assertEqual(calculate_delivery_cost(1, 100, "опасный")[0], 1700)

    def test_express_delivery_halves_cost(self):
        normal_cost = calculate_delivery_cost(1, 1000, "обычный")[0]
        express_cost = calculate_delivery_cost(1, 1000, "обычный", True)[0]
        self.assertEqual(normal_cost, 5200)
        self.assertEqual(express_cost, 2600)

    def test_normal_delivery_days(self):
        self.assertEqual(calculate_delivery_cost(1, 499, "обычный")[1], "2026-09-04")
        self.assertEqual(calculate_delivery_cost(1, 500, "обычный")[1], "2026-09-04")
        self.assertEqual(calculate_delivery_cost(1, 1000, "обычный")[1], "2026-09-05")

    def test_express_delivery_days(self):
        self.assertEqual(
            calculate_delivery_cost(1, 1, "обычный", True)[1],
            "2026-09-03",
        )
        self.assertEqual(
            calculate_delivery_cost(1, 1000, "обычный", True)[1],
            "2026-09-04",
        )

    def test_fractional_cost_is_truncated(self):
        result = calculate_delivery_cost(20, 1, "обычный")
        self.assertEqual(result, (307, "2026-09-04"))


if __name__ == "__main__":
    unittest.main()
