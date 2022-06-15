from django.contrib.auth.backends import AllowAllUsersModelBackend


class CustomModelBackend(AllowAllUsersModelBackend):
    ...
