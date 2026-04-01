from enum import Enum


class Department(str, Enum):
    Support = "Support"
    Sales = "Sales"
    Hr = "Hr"
    It = "It"
    Finance = "Finance"
    Unknown = "Unknown"