import re

from django.contrib.auth import authenticate
from rest_framework import serializers

from authors.apps.profiles.serializers import  AuthenticatedProfileSerializer
from .models import User
from django.shortcuts import get_object_or_404


def validate_password(password):
    if password.isdigit():
        raise serializers.ValidationError(
            'Weak password. The password should contain at least one character'
        )
    elif re.search('[0-9]', password) is None:
        raise serializers.ValidationError(
            'Weak password. The password should contain at least one digit'
        )
    return password


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def validate(self, data):
        """
        This checks if:
        the username is at least 4 characters long
        the username doesn't contain any invalid characters
        the password contains at least 1 number and at least 1 character
        The other validations are done in the User model.
        """
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)

        if not re.match("^[A-Za-z0-9_-]*$", username):
            raise serializers.ValidationError(
                'Username should only contain letters, numbers, underscores and hyphens'
            )

        if len(username) < 4:
            raise serializers.ValidationError(
                'The username should be at least 4 characters long'
            )

        password = validate_password(password)

        return {
            'username': username,
            'email': email,
            'password': password,
        }

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(read_only=True, max_length=255)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token

        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128 
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )


    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token')
        read_only_fields = ('username', 'email')
        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and 
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)


        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()


        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    profile = AuthenticatedProfileSerializer(write_only=True)

    bio = serializers.CharField(source='profile.bio', read_only=True)
    image = serializers.CharField(source='profile.image', read_only=True)
    location = serializers.CharField(source='profile.location', read_only=True)
    occupation = serializers.CharField(source='profile.occupation', read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'profile','bio', 'image', 'location', 'occupation')
        read_only_fields = ('username', 'email')
        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        profile_data = validated_data.pop('profile', {})

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)

        instance.profile.save()

        return instance


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)

    def validate(self, data):
        email = data.get('email', None)
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to reset your password.'
            )

        user = get_object_or_404(User, email=email)
        if user is None:
            raise serializers.ValidationError(
                'This email address is not registered please sign up.'
            )
        return {"id": user.id}


class ComfirmPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    def validate(self, data):
        """
        the password contains at least 1 number and at least 1 character
        """
        password = data.get('password', None)
        password = validate_password(password)

        return {
            'password': password
        }

    def update(self, instance, validated_data):
        """Performs an update on a User."""
        password = validated_data.pop('password', None)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance

class SocialAuthenticationSerializer(serializers.Serializer):
    """Serializers social_auth requests"""
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=1024, required=True, trim_whitespace=True)