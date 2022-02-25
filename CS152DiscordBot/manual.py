from enum import Enum, auto
import discord
import re


class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    AWAITING_SE_RESPONSE = auto()
    MINOR_INVOLVED = auto()
    GROOMING = auto()
    CSAM = auto()
    DELETE_MESSAGE = auto()
    SUSPEND_USER = auto()
    FORWARD_MESSAGE = auto()
    REPORT_COMPLETE = auto()


class Manual:
    START_KEYWORD = ['yes', 'y', 'Yes']
    CANCEL_KEYWORD = ['cancel']
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None

    async def handle_message(self, message):
        '''
        This function makes up the meat of the manual-side reporting flow.
        '''
        if message.content in self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        #REPORT START
        if self.state == State.REPORT_START and message.content in self.START_KEYWORD:
            reply = "Report Started: please answer the following questions to identify further action.\n"
            reply += "Use the `cancel` command at anytime to cancel the report process.\n\n"
            reply += "Does this message contain sexually explicit content?"
            self.state = State.AWAITING_SE_RESPONSE
            return [reply]
        if self.state == State.REPORT_START and message.content not in self.START_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]

        #SE CONTENET
        if self.state == State.AWAITING_SE_RESPONSE and message.content in self.START_KEYWORD:
            reply = "Is a minor involved or referenced?"
            self.state = State.MINOR_INVOLVED
            return [reply]
        if self.state == State.AWAITING_SE_RESPONSE and message.content not in self.START_KEYWORD:
            reply = "Does this message show signs of grooming?"
            self.state = State.GROOMING
            return [reply]

        #MINOR INVOVLED
        if self.state == State.MINOR_INVOLVED and message.content in self.START_KEYWORD:
            reply = "Is CSAM referenced?"
            self.state = State.CSAM
            return [reply]
        if self.state == State.MINOR_INVOLVED and message.content not in self.START_KEYWORD:
            reply = "Would you like to forward this message to a different department?"
            self.state = State.FORWARD_MESSAGE
            return [reply]

        #GROOMING
        if self.state == State.GROOMING and message.content in self.START_KEYWORD:
            reply = "Is a minor involved or referenced?"
            self.state = State.MINOR_INVOLVED
            return [reply]
        if self.state == State.GROOMING and message.content not in self.START_KEYWORD:
            reply = "Would you like to forward this message to a different department?"
            self.state = State.FORWARD_MESSAGE
            return [reply]

        #CSAM
        if self.state == State.CSAM and message.content in self.START_KEYWORD:
            reply = "This message has been forwarded to the authorities.\n"
            reply += "The account will be suspended and message deleted. Report Completed."
            self.state = State.REPORT_COMPLETE
            return [reply]
        if self.state == State.CSAM and message.content not in self.START_KEYWORD:
            reply = "Would you like to delete this message?"
            self.state = State.DELETE_MESSAGE
            return [reply]

        #DELETE MESSAGE
        if self.state == State.DELETE_MESSAGE and message.content in self.START_KEYWORD:
            reply = "This message has been removed. Would you like to suspend this user?"
            self.state = State.SUSPEND_USER
            return [reply]
        if self.state == State.DELETE_MESSAGE and message.content not in self.START_KEYWORD:
            reply = "Would you like to suspend this user?"
            self.state = State.SUSPEND_USER
            return [reply]

        #SUSPEND USER
        if self.state == State.SUSPEND_USER and message.content in self.START_KEYWORD:
            reply = "This user has been suspended. Report Completed."
            self.state = State.REPORT_COMPLETE
            return [reply]
        if self.state == State.SUSPEND_USER and message.content not in self.START_KEYWORD:
            reply = "Report Completed."
            self.state = State.REPORT_COMPLETE
            return [reply]

        #FORWARD MESSAGE
        if self.state == State.FORWARD_MESSAGE and message.content in self.START_KEYWORD:
            reply = "This content has been forwarded. Would you like to delete this message?"
            self.state = State.DELETE_MESSAGE
            return [reply]
        if self.state == State.FORWARD_MESSAGE and message.content not in self.START_KEYWORD:
            reply = "Would you like to delete this message?"
            self.state = State.DELETE_MESSAGE
            return [reply]

        #REPORT COMPLETE
        if self.state == State.REPORT_COMPLETE:
            reply = "Please wait for a new flagged message. Thank you."
            self.state = State.REPORT_COMPLETE
            return [reply]


    def report_complete(self):
        return self.state == State.REPORT_COMPLETE





