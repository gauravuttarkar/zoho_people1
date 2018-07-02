"""
Different functions required for angular
"""
#import uuid

#from django.conf import settings
import json
from django.http import HttpResponse
from django.shortcuts import render
from yellowant import YellowAnt
#from django.urls import reverse
from ..yellowant_api.models import UserIntegration
#from .forms import UserForm
#from django.contrib.auth import authenticate, login
from django.conf import settings

#import requests
# Create your views here.


def index(request, path):
    """Index of the user Integration."""
    context = {
        "user_integrations": [],
        "DJANGO_ENV": settings.DJANGO_ENV
    }

    if request.user.is_authenticated:
        user_integrations = UserIntegration.objects.filter(user=request.user.id)
        #print(user_integration)
        for user_integration in user_integrations:
            context["user_integrations"].append(user_integration)
    #print("test2")
    return render(request, "home.html", context)

def userdetails(request):
    """
    Returns the details of each user in a list.
    """
    user_integrations_list = []
    if request.user.is_authenticated:
        print("Hellow")
        user_integrations = UserIntegration.objects.filter(user=request.user.id)

        for user_integration in user_integrations:
            #print (user_integration.yellowant_integration_invoke_name)
            print (user_integration.id)

            try:
                #print("id :" + user_integration.id)
                smut = UserIntegration.objects.get(id=user_integration.id)
                user_integrations_list.append(
                    {"user_invoke_name":user_integration.yellowant_integration_invoke_name,
                     "id":user_integration.id,
                     "app_authenticated":True, "is_valid":smut.update_login_flag})
                print("Inside try in web/views")
            except: #user_integration.DoesNotExist:
                print("Inside catch")
                user_integrations_list.append({"user_invoke_name": user_integration.yellowant_integration_invoke_name,
                                               "id": user_integration.id, "app_authenticated":True , })
    #print(user_integrations_list)
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")

def delete_integration(request, id=None):
    """Function to delete an integration."""
    #print("In delete_integration")
    #print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    #print(user_integration_id)
    #"https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    UserIntegration.objects.get(yellowant_integration_token=access_token).delete()
    #print(response_json)
    return HttpResponse("successResponse", status=200)


def view_integration(request, id=None):
    """
    Function to View an integration when it is clicked.
    """
    #print("In view_integration")
    #print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    #print(user_integration_id)
    url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    #print(response_json)
    return HttpResponse("successResponse", status=200)
