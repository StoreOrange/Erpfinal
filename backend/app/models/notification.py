from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class EmailConfig(Base):
    __tablename__ = "email_config"

    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String(160), nullable=False, default="")
    sender_name = Column(String(160), nullable=True)
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class NotificationRecipient(Base):
    __tablename__ = "email_recipients"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(160), nullable=False, unique=True)
    name = Column(String(160), nullable=True)
    active = Column(Boolean, default=True)
    procurement_quote_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
