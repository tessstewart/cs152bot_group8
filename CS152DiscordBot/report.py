from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_COMPLETE = auto()

    TYPE_OC = auto()
    TYPE_HARASSMENT = auto()
    TYPE_DANGER = auto()
    MINOR = auto()
    INVOLVE_CHILD = auto()
    TYPE_HARM = auto()

    FOLLOW_UP = auto()
    FURTHER_ACTION = (auto)

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    YES_KEYWORD = 'yes', 'Yes', 'y', 'Y'
    MORE_INFO_KEYWORD = 'more information', 'More information', 'more info', 'yes', 'Yes', 'y', 'Y', '1'
    NO_KEYWORD = 'n', 'N', 'no', 'No', 'Not right now', 'not right now', 'none', 'None', '3'
    RESOURCES_KEYWORD = 'Support resources', 'support resources', '2'
    BLOCK_KEYWORD = 'block', 'Block'
    RESTRICT_KEYWORD = 'Restrict', 'restrict'

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
        self.CSAM_Content = False
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            reply = ["I found this message:", "```" + message.author.name + ": " + message.content + "```", "Please type reason for reporting.\n", "1. Spam \n2. Offensive Content \n3. Harassment \n4. Imminent Danger"]
            return reply

        #Screening Question
        if self.state == State.MESSAGE_IDENTIFIED:
            if message.content in ["Spam", "spam", "1"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action."
                reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
                self.state = State.FURTHER_ACTION
            elif message.content in ["Offensive Content", "offensive content", "2"]:
                reply = "What is the type of offensive content?\n"
                reply += "1. Hate Speech \n2. Copyright Infringement \n3. Glorifying Violence \n" \
                         "4. Sexually Explict Content"
                self.state = State.TYPE_OC
            elif message.content in ["Harassment", "harassment", "3"]:
                reply = "What is the type of harassment?\n"
                reply += "1. Bullying \n2. Hate Speech \n3. Unwanted Sexual Content \n" \
                         "4. Request for Private Information"
                self.state = State.TYPE_HARASSMENT
            elif message.content in ["Imminent Danger", "imminent danger", "4"]:
                reply = "What is the type of danger?\n"
                reply += "1. Self-Harm or Suicide Intent \n2. Threat of Violence"
                self.state = State.TYPE_HARM
            else:
                reply = "I am sorry, I do not understand. Please type one of the following options: \n"
                reply += "1. Spam \n2. Offensive Content \n3. Harassment \n4. Imminent Danger"
            return [reply]

        #Type of offensive content
        if self.state == State.TYPE_OC:
            if message.content in ["Hate Speech", "hate speech", "1", "Copyright Infringement", "copyright infringement",
                                   "2", "Glorifying Violence", "glorifying violence", "3"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action. \n"
                reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
                reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
                self.state = State.FURTHER_ACTION
            elif message.content in ["Sexually Explict Content", "sexually explict content", "4"]:
                reply = "Does this content involve a child? (yes/no/maybe)"
                self.state = State.INVOLVE_CHILD
            else:
                reply = "I am sorry, I do not understand. Please type one of the following options: \n"
                reply += "1. Hate Speech \n2. Copyright Infringement \n3. Glorifying Violence \n" \
                         "4. Sexually Explict Content"
            return [reply]

        #Type of Harassment
        if self.state == State.TYPE_HARASSMENT:
            if message.content in ["Hate Speech", "hate speech", "1", "Bullying", "bullying",
                                   "2"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action. \n"
                reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
                reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
                self.state = State.FURTHER_ACTION
            elif message.content in ["Unwanted Sexual Content", "unwanted sexual content", "3", "request for private information", "4"]:
                reply = "Are you a minor? (yes/no)"
                self.state = State.MINOR
            else:
                reply = "I am sorry, I do not understand. Please type one of the following options: \n"
                reply += "1. Bullying \n2. Hate Speech \n3. Unwanted Sexual Content \n" \
                         "4. Request for Private Information"
            return [reply]

        #Involve Child
        if self.state == State.INVOLVE_CHILD:
            if message.content in ["no", "No", "n"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action. \n"
                reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
                reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
                self.state = State.FURTHER_ACTION
            elif message.content in ["yes", "Yes", "y", "maybe", "Maybe"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action, " \
                        "including removing the content and notifying authorities.\n"
                reply += "Would you would like to learn more about CSAM or receive additional support? \n"
                reply += "1. More Information \n2. Support Resources \n3. Not right now"
                self.state = State.FOLLOW_UP
            else:
                reply = "I am sorry, I do not understand. Please type yes/no/maybe"
            return [reply]

        #Minor
        if self.state == State.MINOR:
            if message.content in ["no", "No", "n"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action. \n"
                reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
                reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
                self.state = State.FURTHER_ACTION
            elif message.content in ["yes", "Yes", "y"]:
                reply = "Thank you for reporting. We will review this content and take the appropriate action, " \
                        "including removing the content and notifying authorities.\n"
                reply += "Would you would like to learn more about CSAM or receive additional support? \n"
                reply += "1. More Information \n2. Support Resources \n3. Not right now"
                self.state = State.FOLLOW_UP
            else:
                reply = "I am sorry, I do not understand. Please type yes/no"
            return [reply]

        if self.state == State.TYPE_HARM:
            reply = "Thank you for reporting. We will review this content and take the appropriate action. \n"
            reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
            reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
            self.state = State.FURTHER_ACTION
            return [reply]

        if self.state == State.FOLLOW_UP and message.content in self.MORE_INFO_KEYWORD:
            reply = "Linking you to more information regarding Child Sexual Abuse Material (CSAM) now\n"
            reply += "https://www.missingkids.org/theissues/csam\n"
            reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
            reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
            self.state = State.FURTHER_ACTION
            return [reply]

        if self.state == State.FOLLOW_UP and message.content in self.NO_KEYWORD:
            reply = "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
            reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
            self.state = State.FURTHER_ACTION
            return [reply]

        if self.state == State.FOLLOW_UP and message.content in self.RESOURCES_KEYWORD:
            reply = "Linking you to support resources regarding Child Sexual Abuse Material (CSAM) now\n"
            reply += "https://www.missingkids.org/gethelpnow/csam-resources\n"
            reply += "We will send you a notification to view the outcome in your Support Requests as soon as possible\n"
            reply += 'Would you like to take further action against this user? (Block, Restrict, or None)'
            self.state = State.FURTHER_ACTION
            return [reply]

        if self.state == State.FURTHER_ACTION and message.content in self.BLOCK_KEYWORD:
            reply = 'This user has been blocked. No further action is needed.'
            self.state = State.REPORT_COMPLETE
            return [reply]

        if self.state == State.FURTHER_ACTION and message.content in self.RESTRICT_KEYWORD:
            reply = "This user's content has been restricted. No further action is needed."
            self.state = State.REPORT_COMPLETE
            return [reply]

        if self.state == State.FURTHER_ACTION and message.content in self.NO_KEYWORD:
            reply = 'No further action has been taken against this user, thank you.'
            self.state = State.REPORT_COMPLETE
            return [reply]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE

    


    

