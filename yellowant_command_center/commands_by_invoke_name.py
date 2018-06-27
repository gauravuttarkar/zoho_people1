"""Mapping for command invoke name to logic"""
from .commands import fetch_all_employees, get_employee, add_employee, get_attendance


COMMANDS_BY_INVOKE_NAME = {
    "fetchallemployees": fetch_all_employees,
    "getemployee": get_employee,
    "addemployee": add_employee,
    "getattendance": get_attendance




}
