"""Urls for YellowAnt related API"""
from django.urls import path

from .views import request_yellowant_oauth_code, yellowant_oauth_redirect, yellowant_api, api_key, webhooks


urlpatterns = [
    path("create-new-integration/", request_yellowant_oauth_code,
         name="request-yellowant-oauth"),
    path("yellowant-oauth-redirect/", yellowant_oauth_redirect,
         name="yellowant-oauth-redirect"),
    path("yellowant-api/", yellowant_api, name="yellowant-api"),
    path("apikey/", api_key, name="api-key"),
    #path("webhooks/<str:id>/(?P<hash_str>[^/]+)/$", webhooks, name="webhooks"),
    path("webhooks/<str:id>/", webhooks, name="webhooks"),
    #path("webhooks/", webhooks, name="webhooks"),
    #path("webhooks/<str:id>/(?P<hash_str>[^/]+)/$", webhooks, name="webhooks"),

]
