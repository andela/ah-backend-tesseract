from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    ComfirmPasswordResetSerializer, RequestPasswordResetSerializer)
from .models import User
from .backends import JWTAuthentication
from .utils import custom_send_mail


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