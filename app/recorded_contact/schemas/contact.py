from marshmallow import Schema, fields, validate, ValidationError

class ContactSchema(Schema):
    fullname = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    email = fields.Email(
        required=True,
        validate=validate.Email()
    )