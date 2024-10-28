from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True)
    email = fields.Email(required=True)
    role_id = fields.Int(required=True)
    active = fields.Bool(required=True)
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
