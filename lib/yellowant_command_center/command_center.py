"""This file contains the logic to understand a user message request from YA and return a response in the format of
a YA message object accordingly
"""
from yellowant.messageformat import MessageClass

from ..yellowant_api.models import UserIntegration
from .commands_by_invoke_name import COMMANDS_BY_INVOKE_NAME


class CommandCenter: #pylint: disable=too-few-public-methods
    """Handles user commands

    Args:
        yellowant_integration_id (int): The integration id of a YA user
        command_name (str): Invoke name of the command the user is calling
        args (dict): Any arguments required for the command to run
    """

    def __init__(self, yellowant_integration_id, command_name, args):
        self.yellowant_integration_id = yellowant_integration_id
        self.command_name = command_name
        self.args = args

        try:
            self.user_integration = UserIntegration.objects.get(
                yellowant_integration_id=self.yellowant_integration_id)
        except UserIntegration.DoesNotExist:
            self.user_integration = None

        self.command = COMMANDS_BY_INVOKE_NAME.get(self.command_name)

    def parse(self):
        """Parse a user command to execute logic

        Handle the inputs from YellowAnt to execute logic which returns a YellowAnt message as a reply.
        """
        message = MessageClass()


        if self.yellowant_integration_id is None:

            message.message_text = "Sorry! I could not find your integration."
            return message

        elif self.command is None:

            message.message_text = "Sorry! I could not find that command."
            return message

        # build YA message object
        #print("Parsing")
        message = self.command(self.args, self.user_integration)

        # use inbuilt sdk method to_json to return message in a json format accepted by YA
        return message.to_json()
