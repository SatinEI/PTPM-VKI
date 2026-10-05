import datetime
import math


INVALID_RESULT = (-1, "0000-00-00")
VALID_PACKAGE_TYPES = ("обычный", "хрупкий", "опасный")


def calculate_delivery_cost(weight: float,distance: int,package_type: str,is_express: bool = False,) -> tuple:

    if not math.isfinite(weight) or not 0.1 <= weight <= 50:
        return INVALID_RESULT

    if not 1 <= distance <= 5000:
        return INVALID_RESULT

    if package_type not in VALID_PACKAGE_TYPES:
        return INVALID_RESULT

    total_cost = 200 + distance * 5

    if 5 < weight < 20:
        total_cost *= 1.2
    elif weight >= 20:
        total_cost *= 1.5

    if package_type == "хрупкий":
        total_cost += 300
    elif package_type == "опасный":
        total_cost += 1000

    if is_express:
        total_cost *= 2

    current_date = datetime.date(2026, 10, 3)

    if is_express:
        days_needed = math.ceil(distance / 1000)
    else:
        days_needed = math.ceil(distance / 500)

    delivery_date = current_date + datetime.timedelta(days=days_needed)
    return int(total_cost), delivery_date.strftime("%Y-%m-%d")
