from enum import StrEnum


class UserRole(StrEnum):
    ELDER = "elder"
    INPUT = "input"
    FAMILY = "family"
    COMMUNITY = "community"
    ADMIN = "admin"
