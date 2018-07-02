import requests
import json



auth_token = '658f6fa024b202772bdea31dc79ecbbf'





def fetch_all_employees():
    url = "https://people.zoho.com/people/api/forms/P_EmployeeView/records?authtoken=" + auth_token
    response = requests.post(url)  
    response = response.json()
    print(type(response))
    print(response)
    for employee in response:
        for k,v in employee.items():
            if k=="First Name":
                first_name = v




def fetch_forms():

    url = 'https://people.zoho.com/people/api/forms?authtoken=' + auth_token


    response = requests.post(url)  
    print(response)
    print(response.text)  



def fetch_employee():
    url = "https://people.zoho.com/people/api/forms/P_EmployeeView/records"
    

    data = {
            'authtoken' : auth_token,
            'searchColumn' : 'EMPLOYEEID',
            'searchValue' : '1'
            }


    response = requests.post(url, data=data)  
    print(response)
    response = response.json()
    print(type(response))
    print(type(response[0]))
    print(response[0])
    #print(response.text)      

dd/MM/yyyy HH:mm:ss

def attendance_check_in():
    url="https://people.zoho.com/people/api/attendance?authtoken=<authtoken>&dateFormat=<dateFormat>&checkIn=\
    &empId=<employeeId>"


def add_employee():   
    # employee_id = args.get('EmployeeID')
    # employee_first_name = args.get('FirstName')
    # employee_last_name = args.get('LastName')
    # auth_token_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.id)
    # auth_token = auth_token_object.auth_token
    url = "https://people.zoho.com/people/api/forms/json/employee/insertRecord"

    data = {
            'EmployeeID': '18',
            'FirstName': 'Robb',
            'LastName': 'Stark',
            'EmailID': 'surdanukni@etoic.com'
            }

    # payload = {
    #     'EmployeeID': employee_id,
    #     'FirstName': employee_first_name,
    #     'LastName': employee_last_name
    # }

    response = requests.post(url, data={"authtoken": auth_token,
                                        "inputData": json.dumps(data)})
    print(response)
    print(response.text)
    response = response.json()
    print(type(response))

    # if (response.json()["response"]["status"]!=0):
    #     print(response["response"]["errors"]["message"])


add_employee() 
#fetch_employee()
# fetch_forms()
{"response":{"result":{"pkId":"442147000000133001","message":"Successfully Added"},"message":"Data added successfully","uri":"/api/forms/json/employee/insertRecord","status":0}}

# fetch_all_employees()
{"response":{"message":"Error occurred","uri":"/api/forms/json/employee/insertRecord","errors":{"code":7400,"message":"Internal Server Error Occured"},"status":1}}

