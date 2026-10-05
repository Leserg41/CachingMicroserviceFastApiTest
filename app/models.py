from sqlalchemy import String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class Payload(Base):
    __tablename__ = "payloads"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)

