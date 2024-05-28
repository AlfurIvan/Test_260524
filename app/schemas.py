from marshmallow import Schema, fields

class RoleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    roles = fields.List(fields.Nested(RoleSchema))
    groups = fields.List(fields.Nested(GroupSchema))