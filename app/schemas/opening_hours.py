from pydantic import BaseModel, Field
from typing import List, Optional

class RegularHour(BaseModel):
    day: str  # monday, tuesday, etc.
    open: Optional[str] = None # HH:MM
    close: Optional[str] = None # HH:MM
    closed: bool = False

class ExceptionHour(BaseModel):
    date: str # YYYY-MM-DD
    label: Optional[str] = None
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False

class OpeningHours(BaseModel):
    timezone: str = "America/Santiago"
    regular: List[RegularHour]
    exceptions: List[ExceptionHour] = []
