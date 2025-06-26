from dataclasses import dataclass


@dataclass
class Vehicle:
    """Represent the status of a vehicle."""

    name: str
    dirt: float
    damage: float
    fuel: float
    fuel_capacity: float
    uses_fuel: bool
