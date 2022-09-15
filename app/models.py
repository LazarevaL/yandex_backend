from cgitb import text
# from http import server
# from sqlite3 import Timestamp
# from unicodedata import name
from .database import Base
from enum import Enum, unique
from sqlalchemy import Column, Integer, ForeignKey, String, Enum as PgEnum, DateTime
# from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
# from sqlalchemy.dialects.postgresql import UUID
# import uuid

@unique
class ItemType(Enum):
    FILE = "file"
    FOLDER = "folder"

class Items(Base):
    __tablename__ = "items"
    # id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    url = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    type = Column(PgEnum(ItemType, name='type'), nullable=False)
    # date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    date = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

class Relations(Base):
    __tablename__ = "relations"
    item_id = Column(Integer, ForeignKey('items.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('items.id', ondelete='CASCADE'), primary_key=True, nullable=False)

# class Imports(Base):
#     __tablename__ = "relations"
#     item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), primary_key=True, nullable=False)
#     parent_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), primary_key=True, nullable=False)