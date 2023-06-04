from django.utils.translation import activate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from user.models import UserProfile


class UserDefinitionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.set_request_user_if_authenticated(request)
        response = self.get_response(request)
        return response

    @staticmethod
    def set_request_user_if_authenticated(request):
        try:
            auth_result = JWTAuthentication().authenticate(request)
        except InvalidToken:
            pass
        else:
            if auth_result:
                request.user = auth_result[0]


class LocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.activate_user_language(request.user)
        response = self.get_response(request)
        return response

    @staticmethod
    def activate_user_language(user):
        try:
            language = UserProfile.objects.get(user=user.id).language
        except UserProfile.DoesNotExist:
            pass
        else:
            if language:
                activate(language)
