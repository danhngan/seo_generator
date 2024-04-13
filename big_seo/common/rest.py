from dataclasses import dataclass

@dataclass
class Response:
    status_code: int
    text: str
    raw_data: bytes

