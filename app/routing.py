from .resources import Register, UserProfile, Login


def initialize_resources(api):
    api.add_resource(Register, '/register')
    api.add_resource(Login, '/login')
    api.add_resource(UserProfile, '/profile')