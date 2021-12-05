from flask import Blueprint, redirect, render_template, url_for, flash, request, session, abort
from flask_login import (login_user, login_required)
from mib.forms.forms import MessageForm
from datetime import date, datetime

from mib.rao.message_manager import MessageManager

msg = Blueprint("message", __name__)



def attachment_get(message_id):  # noqa: E501
    """Retrieves an attachment of a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: InlineResponse2002
    """
    return 'do some magic!'


def delete_received_message(message_id):  # noqa: E501
    """Delete a received message 

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_all_received_messages_metadata():  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def get_all_sent_messages_metadata():  # noqa: E501
    """Get all sent messages metadata of an user

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'

@msg.route('/calendar',methods=['GET'])
def get_calendar():  # noqa: E501
    """Render user's calendar
     # noqa: E501
    :rtype: None
    """
    return render_template("calendar.html")

@msg.route('/message/<message_id>')
def get_message(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    response=MessageManager.get_received_message(message_id)
    if response.status_code==200:
        return response
    if response.status_code==404:
        return abort(404, "Message not found")

    return abort("An error occurred during retrieving the message")
    
@msg.route('/mailbox',methods=['GET'])
def mailbox():  # noqa: E501
    """Render mailboxpage
     # noqa: E501
    :rtype: None
    """
    return render_template("mailbox.html")

@msg.route('/message', methods=["GET, POST"])
def send_message_page():  # noqa: E501
    """Render message page
     # noqa: E501
    :rtype: None
    """
    if request.method=="GET":
        message = ""
        if "message" in session:
            message = session["message"]
            session.pop("message")
        return render_template("send_message.html", message=message, form=MessageForm())
    else:
        send_message()

def _not_valid_string(text):
    return text is None or text == "" or text.isspace()

def send_message(body):  # noqa: E501
    """Send message

     # noqa: E501

    :param body: Send a message
    :type body: dict | bytes

    :rtype: None
    """
    


def delete_message_lottery_points(message_id):  # noqa: E501
    """Delete a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_daily_messages(day, month, year):  # noqa: E501
    """Gets all messages scheduled for a day

     # noqa: E501

    :param day: day
    :type day: int
    :param month: month
    :type month: int
    :param year: year
    :type year: int

    :rtype: List[InlineResponse2003]
    """
    return 'do some magic!'
