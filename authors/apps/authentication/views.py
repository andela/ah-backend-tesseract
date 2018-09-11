from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from authors.apps import ApplicationJSONRenderer as UserJSONRenderer
from social_core.exceptions import MissingBackend
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    ComfirmPasswordResetSerializer, RequestPasswordResetSerializer, SocialAuthenticationSerializer)
from .models import User
from .backends import JWTAuthentication
from .utils import custom_send_mail

from social_django.utils import load_backend, load_strategy


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.data.get('email', None)
        email_subject = "Activate Authors Haven Account"
        custom_send_mail(email, request, 'email_activation.html', email_subject)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActivateAccountAPIView(APIView):

    def get(self, request, user_id, token):
        try:
            user_id = force_text(urlsafe_base64_decode(user_id))
            user = User.objects.get(pk=user_id)

        except(TypeError, ValueError, OverflowError):
            user = None

        auth = JWTAuthentication()
        auth_result = auth.authenticate(request, token=token)
        if user is not None and auth_result[0].id == user.id:
            user.is_active = True
            user.save()
            # login the user
            return Response({"message": "account activated, you can proceed to login"}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):

        email = request.data.get('email', None)
        serializer = self.serializer_class(data={"email": email})
        serializer.is_valid(raise_exception=True)
        email_subject = "Reset Authors Haven's Password"
        message = {"message": "Please check your email for your password reset activation code."}
        custom_send_mail(email, request, "password_reset.html", email_subject)
        return Response(message, status=status.HTTP_200_OK)


class ComfirmPasswordResetAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ComfirmPasswordResetSerializer

    def retrieve(self, request, *args, **kwargs):
        token = get_authorization_header(request).decode("utf-8")
        return Response({"token": token}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = request.data.get('user', {})
        serializer = self.serializer_class(request.user, data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Your password has been reset"}, status=status.HTTP_200_OK)


class SocialAuthenticationAPIView(CreateAPIView):
    """
    Allows for social signup and login using Twitter, Google and Facebook
    """
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthenticationSerializer
    renderer_classes = (UserJSONRenderer,)

    def create(self, request, *args, **kwargs):
        """
        Receives the access_token and provider(facebook, google-oauth2,twitter) from the request,
        once authentication is comlpete, it creates a new user record
        if it does exist already. The user's information (username, email)
        are saved and the user is provided with a JWT token for authorization when
        using our API.
        """
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get('provider')

        access_token = serializer.data.get('access_token')
        user = None if request.user.is_anonymous else request.user

        # strategy sets up the required custom configuration for working with Django
        strategy = load_strategy(request)
        try:
            # Loads backends defined on SOCIAL_AUTH_AUTHENTICATION_BACKENDS,
            # checks the appropiate one by using the provider given
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend:
            return Response({
                "errors": {
                    "provider": ["Invalid provider"]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # creates a user in our user model 
            # If the user exists, we just authenticate the user.
            user = backend.do_auth(access_token, user=user)

        except BaseException as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        # Since the user is using social authentication, there is no need for email verification.
        # We therefore set the user to active here.

        user.is_active = True

        user.save()

        serializer = UserSerializer(user)
    
        return Response(serializer.data, status=status.HTTP_200_OK)