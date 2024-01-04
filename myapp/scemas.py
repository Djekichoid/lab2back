from marshmallow import Schema, fields, validate, ValidationError


class CategorySchema(Schema):
    name = fields.String(required=True)
class RecordSchema(Schema):
    category_id = fields.Integer(required=True, validate=validate.Range(min=0))
    user_id = fields.Integer(required=True, validate=validate.Range(min=0))
    amount = fields.Float(required=True, validate=validate.Range(min=0.0))
class IncomeAccountSchema(Schema):
    balance = fields.Float(required=True, validate=validate.Range(min=0.0, error="Balance must be a non-negative number"))


class UserSchema(Schema):
    username = fields.String(required=True)
    income_account = fields.Nested(IncomeAccountSchema)
