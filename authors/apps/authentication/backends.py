import jwt

from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication

from authors.apps.authentication.models import User
from authors.settings import SECRET_KEY


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        token = get_authorization_header(request)

        if not token:
            return None

        try:
            decoded = jwt.decode(token, SECRET_KEY)

            user_id = decoded["id"]
            username = decoded["username"]
            user = User.objects.get(id=user_id, username=username)

            return user, token

        except jwt.InvalidTokenError or jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Invalid token ")

        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed("Token expired Login again to get new token")
