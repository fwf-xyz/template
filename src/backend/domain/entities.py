import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class Note:
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
