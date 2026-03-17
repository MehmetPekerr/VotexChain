from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    data = Column(JSON, nullable=False)
    previous_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False, unique=True)
    nonce = Column(Integer, nullable=False)
    transactions = relationship("Transaction", back_populates="block", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('index', name='uix_block_index'),
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String, unique=True, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    block = relationship("Block", back_populates="transactions")
    
    __table_args__ = (
        UniqueConstraint('transaction_hash', name='uix_transaction_hash'),
    ) 