from enum import Enum


class IngestionStatus(str, Enum):
    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    ERROR = "error"

