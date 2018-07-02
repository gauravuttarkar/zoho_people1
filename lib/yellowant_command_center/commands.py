"""Code which actually takes care of application API calls or other business logic"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass ,MessageButtonsClass
from ..yellowant_api.models import UserIntegration
import uuid
import requests
import json
from yellowant import YellowAnt
from django.conf import settings


def get_attendance(args,user_integration):
    auth_token_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    auth_token = auth_token_object.auth_token
    m = MessageClass()

    url = 'https://people.zoho.com/people/api/attendance/getUserReport?'

    sDate = args.get('start_date')
    eDate = args.get('end_date')
    employee_id = args.get('employee_id')

    data = {
            'authtoken' : auth_token,
            'sdate' : sDate,
            'edate' : eDate,
            'empId' : employee_id,
            'dateFormat': 'yyyy-MM-dd'
            }

    response = requests.post(url,data=data)
    response = response.json()
    print(type(response))
    attachment = MessageAttachmentsClass()

    for k,v in response.items():
        attachment = MessageAttachmentsClass()
        attachment.title = k
        for k1,v1 in v.items():
            field = AttachmentFieldsClass()
            field.title = k1
            field.value = v1
            attachment.attach_field(field)
        m.attach(attachment)



        field = AttachmentFieldsClass()


    print(response)

    print(sDate)
    print(eDate)
    print(employee_id)

    m.message_text = "Just test"

    return m



def get_employee(args,user_integration):

    employee_id = args.get('employee_id')
    auth_token_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    auth_token = auth_token_object.auth_token
    m = MessageClass()
    m.message_text = "The Employee details are:"
    url = "https://people.zoho.com/people/api/forms/P_EmployeeView/records"
    data = {
            'authtoken' : auth_token,
            'searchColumn' : 'EMPLOYEEID',
            'searchValue' : employee_id
            }

    attachment = MessageAttachmentsClass()

    response = requests.post(url, data=data)
    response = response.json()

    field = AttachmentFieldsClass()
    field.title = "First Name"
    field.value = response[0]['First Name']

    field1= AttachmentFieldsClass()
    field1.title = "Last Name"
    field1.value = response[0]['Last Name']

    field2 = AttachmentFieldsClass()
    field2.title = "Email"
    field2.value = response[0]['Email ID']

    field3 = AttachmentFieldsClass()
    field3.title = "EmployeeID"
    field3.value = response[0]['EmployeeID']

    attachment.attach_field(field)
    attachment.attach_field(field1)
    attachment.attach_field(field2)
    attachment.attach_field(field3)


    attachment.image_url = response[0]['Photo']

    m.attach(attachment)



    return m

def fetch_all_employees(args,user_integration):
    print(user_integration.yellowant_integration_id)
    print("user",user_integration.id)
    auth_token_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    auth_token = auth_token_object.auth_token
    data = {'list': []}
    url = "https://people.zoho.com/people/api/forms/P_EmployeeView/records?authtoken=" + auth_token
    response = requests.post(url)
    response = response.json()
    m = MessageClass()
    for employee in response:
        attachment = MessageAttachmentsClass()
        for k,v in employee.items():
            if k=="First Name":
                field1 = AttachmentFieldsClass()
                field1.title = "First Name"
                field1.value = v
                attachment.attach_field(field1)
                first_name = v
            if k=="Last Name":
                field2 = AttachmentFieldsClass()
                field2.title = "Last Name"
                field2.value = v
                attachment.attach_field(field2)
                last_name = v
            if k=="EmployeeID":
                field3 = AttachmentFieldsClass()
                field3.title = "EmployeeID"
                field3.value = v
                attachment.attach_field(field3)
                employee_id = v
            if k=="recordId":
                record_id = v

        button = MessageButtonsClass()
        button.text = "Get details"
        button.value = "Get details"
        button.name = "Get details"
        button.command = {"service_application": str(user_integration.yellowant_integration_id),
                          "function_name": "getemployee", "data": {"employee_id": employee_id},
                          }
        attachment.attach_button(button)

        data['list'].append({"record_id": record_id , "employee_id": employee_id, "employee_name": first_name + " " + last_name })

        m.data = data
        m.attach(attachment)


    m.message_text = "Employee details are:"



    return m

def add_employee(args,user_integration):
    employee_id = args.get('EmployeeID')
    employee_first_name = args.get('FirstName')
    employee_last_name = args.get('LastName')
    employee_email = args.get('EmailID')

    auth_token_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    auth_token = auth_token_object.auth_token
    print(auth_token)
    url = "https://people.zoho.com/people/api/forms/json/employee/insertRecord"
    m = MessageClass()
    data = {
            'EmployeeID': employee_id,
            'FirstName': employee_first_name,
            'LastName': employee_last_name,
            'EmailID': employee_email
            }


    response = requests.post(url, data={"authtoken": auth_token,
                                        "inputData": json.dumps(data)})
    print(response.text)
    print(type(response))
    response = response.json()
    print(type(response))

    if (response['response']['status']==0):
        print('Done successfully')
        print(response['response']['message'])
        m.message_text = response['response']['message']

    else:
        print(response["response"]["message"])
        print(response["response"]["errors"]["message"])
        m.message_text = response["response"]["errors"]["message"]





    print(response)

    return m














