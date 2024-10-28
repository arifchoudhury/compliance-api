from marshmallow import Schema, fields, validate, ValidationError

class AttributeSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    regex = fields.String(
        validate=validate.Length(min=1, max=100)  # Optional fields do not need 'required'
    )
    required = fields.Boolean()
    unique = fields.Boolean()