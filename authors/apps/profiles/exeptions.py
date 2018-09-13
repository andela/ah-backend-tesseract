from rest_framework.exceptions import APIException


class UserDoesNotExist(APIException):
    status_code = 404
    default_detail = 'A profile with this username was not found.'