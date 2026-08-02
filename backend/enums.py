from enum import StrEnum

class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"

class PlacementStatus(StrEnum):
    ONBOARDING = "ONBOARDING"
    TRAINING = "TRAINING"
    AVAILABLE = "AVAILABLE"
    PLACED = "PLACED"