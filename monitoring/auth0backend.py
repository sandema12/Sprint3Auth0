import requests
from social_core.backends.oauth import BaseOAuth2
from django.conf import settings


class Auth0(BaseOAuth2):
    """
    Backend de autenticación para usar Auth0 con social-auth.
    """
    name = "auth0"
    SCOPE_SEPARATOR = " "
    ACCESS_TOKEN_METHOD = "POST"
    EXTRA_DATA = [
        ("picture", "picture"),
    ]

    def authorization_url(self):
        return "https://" + settings.SOCIAL_AUTH_AUTH0_DOMAIN + "/authorize"

    def access_token_url(self):
        return "https://" + settings.SOCIAL_AUTH_AUTH0_DOMAIN + "/oauth/token"

    def get_user_id(self, details, response):
        return details["user_id"]

    def get_user_details(self, response):
        url = "https://{domain}/userinfo".format(
            domain=settings.SOCIAL_AUTH_AUTH0_DOMAIN
        )
        headers = {"authorization": "Bearer " + response["access_token"]}
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()

        return {
            "username": userinfo.get("nickname", ""),
            "first_name": userinfo.get("name", ""),
            "picture": userinfo.get("picture", ""),
            "user_id": userinfo.get("sub"),
        }


def getRole(request):
    """
    Obtiene el rol del usuario autenticado desde el token de Auth0.
    El rol debe estar configurado como custom claim en app_metadata
    bajo la clave "<dominio_auth0>/role".
    """
    user = request.user
    auth0user = user.social_auth.filter(provider="auth0")[0]
    access_token = auth0user.extra_data["access_token"]

    url = "https://{domain}/userinfo".format(
        domain=settings.SOCIAL_AUTH_AUTH0_DOMAIN
    )
    headers = {"authorization": "Bearer " + access_token}
    resp = requests.get(url, headers=headers)
    userinfo = resp.json()

    claim_key = settings.SOCIAL_AUTH_AUTH0_DOMAIN + "/role"
    return userinfo.get(claim_key, "SIN_ROL")
