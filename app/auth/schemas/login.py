from marshmallow import Schema, fields, ValidationError, validates

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    
    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")
