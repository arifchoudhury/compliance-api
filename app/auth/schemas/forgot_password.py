from marshmallow import Schema, fields, ValidationError, validates

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)
