# coding: utf-8

from .models import ScriptExecution
import datetime
import sys


# from please_marketing_script_execution.log_script import *
def log_script(name, status):

    ScriptExecution(
        script_name=name,
        status=status,
    ).save()

    return


# from please_marketing_script_execution.log_script import log_script
# log_script(name="executor_update_amplitude_users", status="s")
