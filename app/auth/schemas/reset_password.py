from marshmallow import Schema, fields, ValidationError, validates

class ResetPasswordSchema(Schema):
    reset_token = fields.Str(required=True)
    new_password = fields.Str(required=True)

    @validates('new_password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
