"""Views for the API urls"""
import json
import uuid
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass ,MessageButtonsClass
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, \
    HttpResponseBadRequest
from django.contrib.auth.models import User
from django.conf import settings

import requests
from django.urls import reverse
from yellowant import YellowAnt

from ..yellowant_command_center.command_center import CommandCenter
from ..yellowant_api.models import YellowAntRedirectState, UserIntegration


def request_yellowant_oauth_code(request):
    """Initiate the creation of a new user integration on YA

    YA uses oauth2 as its authorization framework. This method requests for an oauth2 code from YA
    to start creating a new user integration for this application on YA.
    """
    # get the user requesting to create a new YA integration
    user = User.objects.get(id=request.user.id)

    # generate a unique ID to identify the user when YA returns an oauth2 code
    state = str(uuid.uuid4())
    print("Inside request")
    print(state)
    # save the relation between user and state so that we can identify the user when YA returns the
    # oauth2 code
    YellowAntRedirectState.objects.create(user=user, state=state)

    # Redirect the application user to the YA authentication page. Note that we are passing state,
    # this app's client id, oauth response type as code, and the url to return the oauth2 code at.
    return HttpResponseRedirect("{}?state={}&client_id={}&response_type=code&redirect_url={}"
                                .format(settings.YA_OAUTH_URL, state, settings.YA_CLIENT_ID, settings.YA_REDIRECT_URL))


def yellowant_oauth_redirect(request):
    """Receive the oauth2 code from YA to generate a new user integration

    This method calls utilizes the YA Python SDK to create a new user integration on YA.
    This method only provides the code for creating a new user integration on YA. Beyond that, you
    might need to authenticate the user on the actual application (whose APIs this application will
    be calling) and store a relation between these user auth details and the YA user integration.
    """
    # oauth2 code from YA, passed as GET params in the url
    code = request.GET.get("code")

    # the unique string to identify the user for which we will create an integration
    state = request.GET.get("state")

    # fetch user with the help of state
    yellowant_redirect_state = YellowAntRedirectState.objects.get(state=state)
    user = yellowant_redirect_state.user

    # initialize the YA SDK client with your application credentials
    ya_client = YellowAnt(app_key=settings.YA_CLIENT_ID, app_secret=settings.YA_CLIENT_SECRET,
                          access_token=None, redirect_uri=settings.YA_REDIRECT_URL)

    # get the access token for a user integration from YA against the code
    access_token_dict = ya_client.get_access_token(code)
    print(access_token_dict)
    access_token = access_token_dict["access_token"]

    # reinitialize the YA SDK client with the user integration access token
    ya_client = YellowAnt(access_token=access_token)

    # get YA user details
    ya_user = ya_client.get_user_profile()
    webhook_id = str(uuid.uuid4())
    # create a new user integration for your application
    user_integration = ya_client.create_user_integration()

    # save the YA user integration details in your database
    UserIntegration.objects.create(
        user=user, yellowant_user_id=ya_user["id"],
        yellowant_team_subdomain=ya_user["team"]["domain_name"],
        yellowant_integration_id=user_integration["user_application"],
        yellowant_integration_invoke_name=user_integration["user_invoke_name"],
        yellowant_integration_token=access_token,
        webhook_id = webhook_id
    )

    # A new YA user integration has been created and the details have been successfully saved in
    # your application's database. However, we have only created an integration on YA. As a
    # developer, you need to begin an authentication process for the actual application, whose API
    # this application is connecting to. Once, the authentication process for the actual application
    # is completed with the user, you need to create a db entry which relates the YA user
    # integration, we just created, with the actual application authentication details of the user.
    # This application will then be able to identify the actual application accounts corresponding
    # to each YA user integration.

    # return HttpResponseRedirect("to the actual application authentication URL")

    return HttpResponseRedirect("/")


def yellowant_api(request):
    """Receive user commands from YA"""
    try:
        data = json.loads(request.POST.get("data"))
    except TypeError:
        data = json.loads(request.body)["data"]

    # verify whether the request is genuinely from YA with the help of the verification token
    if data["verification_token"] != settings.YA_VERIFICATION_TOKEN:
        return HttpResponseNotAllowed("Insufficient permissions.")

    # check whether the request is a user command, or a webhook subscription notice from YA
    if data["event_type"] == "command":
        # request is a user command

        # retrieve the user integration id to identify the user
        yellowant_integration_id = data.get("application")

        # invoke name of the command being called by the user
        command_name = data.get("function_name")

        # any arguments that might be present as an input for the command
        args = data.get("args")


        # create a YA Message object with the help of the YA SDK
        message = CommandCenter(yellowant_integration_id,
                                command_name, args).parse()

        # return YA Message object back to YA
        return HttpResponse(message)
    elif data["event_type"] == "webhook_subscription":
        # request is a webhook subscription notice
        # TODO: Complete logic for webhook subscription
        return HttpResponse("")

    return HttpResponseBadRequest("Invalid request")


def api_key(request):
    """An object is created in the database using the request."""
    data = json.loads(request.body)

    object = UserIntegration.objects.get(id=data['user_integration_id'])
    auth_token = data['auth_token']

    response=requests.post(url="https://people.zoho.com/people/api/forms?authtoken="+auth_token)
    if response.status_code != 200:
        return HttpResponse("Failed", status=response.status_code)

    object.update_login_flag = True
    object.auth_token = auth_token
    object.save()


    return HttpResponse("Success", status=200)

def webhooks(request, id=None):
    """
        This function handles the incoming webhooks.
    """
    print(request.body)

    event_type = request.POST.get('event_type')
    print(event_type)
    print(type(event_type))

    if event_type == "created":
        # print("in pipeline webhook")
        employee_created(request, id)

    elif event_type == "deleted":
        # print("in user webhook")
        print("Inside elif")
        employee_deleted(request, id)

    elif event_type == "invoice":
        # print("in deal webhook")
        add_new_invoice(request, id)

    return HttpResponse("OK", status=200)


def employee_deleted(request,id):
    print('Inside employee delete')
    name = request.POST['name']
    contact_id = request.POST['id']
    last_name = request.POST['last_name']
    email = request.POST['email']

    yellow_obj = UserIntegration.objects.get(webhook_id=id)
    access_token = yellow_obj.yellowant_integration_token
    integration_id = yellow_obj.yellowant_integration_id
    service_application = str(integration_id)

    # Creating message object for webhook message
    webhook_message = MessageClass()
    webhook_message.message_text = "Employee details deleted"
    attachment = MessageAttachmentsClass()

    field = AttachmentFieldsClass()
    field.title = "Name"
    field.value = name + " " + last_name

    attachment.attach_field(field)

    field1 = AttachmentFieldsClass()
    field1.title = "Email ID"
    field1.value = email

    attachment.attach_field(field1)

    # print(integration_id)
    webhook_message.data = {
        "Name": name,
        "ID": contact_id,
        "Email": email,
        "LastName": last_name
    }
    webhook_message.attach(attachment)
    # Creating yellowant object
    yellowant_user_integration_object = YellowAnt(access_token=access_token)

    # Sending webhook message to user
    send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=service_application,
        webhook_name="deleteemployeewebhook", **webhook_message.get_dict())
    return HttpResponse("OK", status=200)


def employee_created(request,id):

    print('Inside employee created')
    name = request.POST['name']
    contact_id = request.POST['id']
    last_name = request.POST['last_name']
    email = request.POST['email']

    yellow_obj = UserIntegration.objects.get(webhook_id=id)
    access_token = yellow_obj.yellowant_integration_token
    integration_id = yellow_obj.yellowant_integration_id
    service_application = str(integration_id)

    # Creating message object for webhook message
    webhook_message = MessageClass()
    webhook_message.message_text = "New Employee added"
    attachment = MessageAttachmentsClass()

    field = AttachmentFieldsClass()
    field.title = "Name"
    field.value = name + " " + last_name

    attachment.attach_field(field)

    field1 = AttachmentFieldsClass()
    field1.title = "Email ID"
    field1.value = email

    attachment.attach_field(field1)

    # print(integration_id)
    webhook_message.data = {
        "Name": name,
        "ID": contact_id,
        "Email": email,
        "LastName": last_name
    }
    webhook_message.attach(attachment)
    # Creating yellowant object
    yellowant_user_integration_object = YellowAnt(access_token=access_token)

    # Sending webhook message to user
    send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=service_application,
        webhook_name="createemployeewebhook", **webhook_message.get_dict())
    return HttpResponse("OK", status=200)


