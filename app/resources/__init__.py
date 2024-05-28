from .auth import Register, UserProfile, Login
from .users import UserList, UserDetail


def initialize_resources(api):
    api.add_resource(Register, '/register')
    api.add_resource(Login, '/login')
    api.add_resource(UserProfile, '/profile')

    api.add_resource(UserList, '/users')
    api.add_resource(UserDetail, '/users/<int:user_id>')
