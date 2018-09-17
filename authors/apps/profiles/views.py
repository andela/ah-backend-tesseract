from .exeptions import UserDoesNotExist
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView

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

        serializer = self.serializer_class(profile,context={
            'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = AuthenticatedProfileSerializer

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            user_to_follow = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise UserDoesNotExist

        if follower.pk is user_to_follow.pk:
            raise serializers.ValidationError('You can not follow yourself.')

        follower.follow(user_to_follow)

        serializer = self.serializer_class(follower, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise UserDoesNotExist

        follower.unfollow(followed)

        serializer = self.serializer_class(followed, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuthenticatedProfileSerializer

    def get(self, request):
        users_profiles = Profile.objects.all().exclude(pk=request.user.id)
        serializer = self.serializer_class(users_profiles, many=True)
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)
