"""
SQLAlchemy model for the nodes table.

Table: nodes
- id: SERIAL PRIMARY KEY
- name: VARCHAR UNIQUE NOT NULL
- host: VARCHAR NOT NULL
- port: INTEGER NOT NULL
- status: VARCHAR DEFAULT 'active'
- created_at: TIMESTAMP DEFAULT NOW()
- updated_at: TIMESTAMP DEFAULT NOW()
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from src.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
