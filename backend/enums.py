from enum import StrEnum

class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"

class PlacementStatus(StrEnum):
    ONBOARDING = "ONBOARDING"
    TRAINING = "TRAINING"
    AVAILABLE = "AVAILABLE"
    PLACED = "PLACED"
    ENDING_SOON = "ENDING_SOON"

class Batch(StrEnum):
    PYTHON = "PYTHON"
    JAVA = "JAVA"
    DATA = "DATA"
    ANDRIOD = "ANDROID"    
    #
    #
    #