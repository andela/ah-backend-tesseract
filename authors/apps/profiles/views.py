from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer, AuthenticatedProfileSerializer


class ProfileAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):

        profile =get_object_or_404(Profile, user__username=username)

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthentivatedProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = AuthenticatedProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):

        profile =get_object_or_404(Profile, user__username=username)

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)