"""
API Key model for authentication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)

    # API Key
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # Friendly name for the key

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status and limits
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)

    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="api_keys")
