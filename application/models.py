from sqlalchemy import (
    Column, Integer, String, ForeignKey, Float, DateTime, Boolean,
    Index, CheckConstraint, Enum
)
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid import uuid4

from app import db
from application.default import OperationType, UserStatus, AccountStatus, OperationStatus


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def last_updated(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False)


class Currency(db.Model, TimestampMixin):
    __tablename__ = 'currencies'

    name = Column(String, primary_key=True, unique=True)


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    # Add other fields to maintain user information!!
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.CREATED)
    password = Column(String, nullable=False)
    profile = Column(String, nullable=False, default="user")

    accounts = relationship('Account', backref='user', lazy='dynamic')


class Account(db.Model, TimestampMixin):
    __tablename__ = 'accounts'

    id = Column(UUID, primary_key=True)
    alias = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.CREATED)
    currency_name = Column(String, ForeignKey('currencies.name'), nullable=False)
    total = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        CheckConstraint('total >= 0', name='check_total_positive'),
    )


class Transaction(db.Model, TimestampMixin):
    __tablename__ = 'transactions'

    id = Column(UUID, primary_key=True)
    linked_transaction_id = Column(UUID, nullable=True)  # intentionally possible could be blank
    amount = Column(Float, nullable=False)
    total = Column(Float, nullable=True)
    operation = Column(Enum(OperationType), nullable=False)
    operation_status = Column(Enum(OperationStatus), nullable=False, default=OperationStatus.CREATED)
    origin_account_id = Column(UUID, ForeignKey('accounts.id'), nullable=False)
    destination_account_id = Column(UUID, ForeignKey('accounts.id'), nullable=False)
    currency_name = Column(String, ForeignKey('currencies.name'), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    reference = Column(String, nullable=True)



# Event listeners to ensure that created_at and last_updated are always set correctly
@event.listens_for(db.Model, 'before_insert', propagate=True)
def before_insert(mapper, connection, target):
    target.id = str(uuid4())


@event.listens_for(db.Model, 'before_update', propagate=True)
def before_update(mapper, connection, target):
    pass
