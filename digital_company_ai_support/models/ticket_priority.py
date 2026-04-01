from enum import Enum


class TicketPriority(str, Enum):
    Low = "Low"
    Normal = "Normal"
    High = "High"
    Critical = "Critical"