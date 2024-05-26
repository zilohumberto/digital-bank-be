from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_enum import EnumField

from application.default import AccountStatus, UserStatus, OperationStatus, OperationType

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str()
    status = EnumField(UserStatus, by_value=True)
    is_deleted = fields.Bool(dump_only=True)
    profile = fields.Str(dump_only=True)

    creation_time = fields.Method("format_date", dump_only=True)
    last_updated = fields.Method("format_date", dump_only=True)

    def format_date(self, obj):
        return obj.last_updated.strftime("%d/%m/%Y")


class UserUpdateSchema(UserSchema):
    name = fields.Str()
    email = fields.Email()


class LoginSchema(Schema):
    password = fields.Str(required=True)
    email = fields.Email(required=True)


class TransactionSchema(Schema):
    id = fields.UUID(dump_only=True)
    total = fields.Float(dump_only=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    operation = EnumField(OperationType, by_value=True, required=True)
    operation_status = EnumField(OperationStatus, by_value=True, dump_only=True)
    origin_account_id = fields.UUID(required=True)
    destination_account_id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    currency_name = fields.Str(required=True)
    linked_transaction_id = fields.UUID(dump_only=True)
    reference = fields.Str(required=False)

    creation_time = fields.Method("format_date", dump_only=True)
    last_updated = fields.Method("format_date", dump_only=True)

    def format_date(self, obj):
        return obj.last_updated.strftime("%d/%m/%Y")


class AccountSchema(Schema):
    id = fields.UUID(dump_only=True)
    alias = fields.Str(required=True)
    status = EnumField(AccountStatus, by_value=True)
    user_id = fields.UUID()
    currency_name = fields.Str(required=True)
    total = fields.Float(dump_only=True)

    creation_time = fields.Method("format_date", dump_only=True)
    last_updated = fields.Method("format_date", dump_only=True)

    def format_date(self, obj):
        return obj.last_updated.strftime("%d/%m/%Y")

class CurrencySchema(Schema):
    name = fields.Str(required=True)
