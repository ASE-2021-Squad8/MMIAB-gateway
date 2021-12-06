from flask import (
    Blueprint,
    json,
    redirect,
    render_template,
    url_for,
    request,
    session,
    abort,
    jsonify,
)
from flask_login import login_required, current_user
from mib.forms.forms import MessageForm
from mib.rao.user_manager import UserManager
from datetime import datetime
import os
import json
import base64
from re import search

from mib.rao.message_manager import MessageManager

msg = Blueprint("message", __name__)
ERROR_PAGE = "error_page"


@msg.route("/message/<message_id>/attachment")
def attachment_get(message_id):  # noqa: E501
    """Retrieves an attachment of a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: InlineResponse2002
    """
    response = MessageManager.get_attachment(message_id)

    if response.status_code == 200:
        json_obj = response.get_json()
        data_response = {"attachment": json_obj["media"]}
        return jsonify(data_response)
    else:
        return abort(500)


@msg.route("/message/bin/<message_id>", methods=["DELETE"])
@login_required
def delete_received_message(message_id):  # noqa: E501
    """Delete a received message
     # noqa: E501
    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    user_id = current_user.id
    response = MessageManager.set_message_is_delete(message_id, user_id)
    if response.status_code == 200:
        return jsonify({"message_id": message_id})
    else:
        return abort(500)


@msg.route("/received/metadata")
def get_all_received_messages_metadata():  # noqa: E501
    """Get all receied messages metadata of an user
     # noqa: E501
    :rtype: List[MessageMetadata]
    """
    user_id = current_user.id
    response = MessageManager.get_received_messages_metadata(user_id)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return abort(
            response.status_code, "An error occured while retrieving the metadata"
        )


@msg.route("/sent/metadata", methods=["GET"])
@login_required
def get_all_sent_messages_metadata():  # noqa: E501
    """Get all sent messages metadata of an user
     # noqa: E501
    :rtype: List[MessageMetadata]
    """
    user_id = current_user.id
    response = MessageManager.get_sent_messages_metadata(user_id)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return abort(
            response.status_code, "An error occured while retrieving the metadata"
        )


@msg.route("/calendar", methods=["GET"])
@login_required
def get_calendar():  # noqa: E501
    """Render user's calendar
     # noqa: E501
    :rtype: None
    """
    return render_template("calendar.html")


@msg.route("/message/<message_id>")
def get_message(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    response = MessageManager.get_message(message_id)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return abort(500)


@msg.route("/message/mailbox", methods=["GET"])
@login_required
def mailbox():  # noqa: E501
    """Render mailboxpage
     # noqa: E501
    :rtype: None
    """
    return render_template("mailbox.html")


@msg.route("/message", methods=["GET", "POST"])
@login_required
def send_message():  # noqa: E501
    """Render message page
     # noqa: E501
    :rtype: None
    """
    if request.method == "GET":
        message = ""
        if "message" in session:
            message = session["message"]
            session.pop("message")
        return render_template("send_message.html", message=message, form=MessageForm())
    else:
        now = datetime.now()
        s_date = request.form["delivery_date"]
        delivery_date = (
            datetime.fromisoformat(s_date) if not _not_valid_string(s_date) else None
        )
        # check parameters
        if delivery_date is None or delivery_date < now:
            return _get_result(
                None, "/send_message", True, 400, "Delivery date in the past"
            )
        if _not_valid_string(request.form["text"]):
            return _get_result(
                None, "/send_message", True, 400, "Message to send cannot be empty"
            )

        recipients = request.form.getlist("recipient")
        if recipients == [] or recipients is None:
            return _get_result(
                None, "/send_message", True, 400, "Message needs at least one recipient"
            )

        errors = 0
        for recipient in recipients:
            # Check if the message is a draft
            msg = dict()
            msg["delivery_date"] = delivery_date
            msg["text"] = request.form["text"]
            msg["sender"] = int(current_user.id)
            msg["recipient"] = int(recipient)
            msg["message_id"] = request.form["draft_id"]
            msg["media"] = ""

            # Check the attachment
            if (
                "attachment" in request.files
                and request.files["attachment"].filename != ""
            ):
                file = request.files["attachment"]

                if _extension_allowed(file.filename):
                    msg["media"] = base64.b64encode(file).decode("utf-8")
                else:
                    return _get_result(
                        None, ERROR_PAGE, True, 400, "File extension not allowed"
                    )

            # send message
            response = MessageManager.send_message(json.dumps(msg))
            if response.status_code != 201:
                errors += 1

        if errors > 0:
            return _get_result(None, ERROR_PAGE, True, 500, "Internal server error")
        else:
            return _get_result(
                jsonify({"message sent": True}),
                "message.send_message",
                message="Message sent successfully!",
            )


@msg.route("/lottery/<message_id>", methods=["DELETE"])
def delete_message_lottery_points(message_id):  # noqa: E501
    """Delete a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    response = MessageManager.delete_message_lottery_points(message_id)
    if response.status_code == 200:
        return jsonify({"message_id": message_id})
    else:
        # error 400, 401, 404
        return jsonify({"message_id": -1})


@msg.route("/api/calendar/<int:day>/<int:month>/<int:year>", methods=["GET"])
@login_required
def get_daily_messages(day: int, month: int, year: int):  # noqa: E501
    """Gets all messages scheduled for a day
     # noqa: E501
    :param day: day
    :type day: int
    :param month: month
    :type month: int
    :param year: year
    :type year: int
    :rtype: List[messages]
    """

    if day > 31 or month + 1 > 12:
        return _get_result(None, ERROR_PAGE, True, 404, "Invalid date")
    else:
        response = MessageManager.get_day_message(year, month, day, current_user.id)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return jsonify(dict())
        else:
            return abort(500)


@msg.route("/message/draft", methods=["GET"])
def get_all_drafts():
    """Get all the drafts for the current user"""
    response = MessageManager.get_all_drafts_for_user(current_user.id)
    if response.status_code == 200:
        return response.json()
    else:
        return abort(500)


@msg.route("/message/draft", methods=["POST"])
def save_draft():
    """Save a new draft"""
    draft = dict()
    draft_id = request.form["draft_id"]
    if _not_valid_string(request.form["text"]):
        return _get_result(
            None, ERROR_PAGE, True, 400, "Message to draft cannot be empty"
        )
    date = request.form["delivery_date"]
    draft["delivery_date"] = (
        datetime.fromisoformat(date) if not _not_valid_string(date) else None
    )
    draft["text"] = request.form["text"]
    draft["sender"] = current_user.id
    if "recipient" in request.form and request.form["recipient"] != "":
        draft["recipient"] = request.form["recipient"]

    # Check the attachment
    if "attachment" in request.files and request.files["attachment"].filename != "":
        file = request.files["attachment"]

        if _extension_allowed(file.filename):
            draft["media"] = base64.b64encode(file).decode("utf-8")
        else:
            return _get_result(
                None, ERROR_PAGE, True, 400, "File extension not allowed"
            )

    # Send the draft to the message ms
    if draft_id != "" and draft_id is not None:
        response = MessageManager.update_draft(draft_id, json.dumps(draft))
    else:
        response = MessageManager.save_new_draft(json.dumps(draft))

    if response.status_code == 200:
        return _get_result(jsonify({"message_id": draft_id}), "message.send_message")
    else:
        return _get_result(None, ERROR_PAGE, True, 500, "Internal server error")


@msg.route("/api/message/read_message/<id>")
def read_msg(id):
    """
    Read the message with id and send a notification to the sender
    """
    response = MessageManager.get_message(id)
    msg = response.json()
    if response.status_code == 200:
        if not msg["is_read"]:
            # If it's the first time reading the message, send a notification to the message sender
            response = MessageManager.update_message(id, "is_read", True)
            if response.status_code == 200:
                response = UserManager.get_user_email(msg["sender"])
                if response.status_code == 200:
                    sender = response.json()["email"]
                response = UserManager.get_user_email(msg["recipient"])
                if response.status_code == 200:
                    receiver = response.json()["email"]
                MessageManager.send_notification(sender, receiver)
            elif response.status_code == 404:
                return abort(
                    404, json.dumps({"msg_read": False, "error": "message not found"})
                )
            else:
                return abort(
                    500,
                    json.dumps(
                        {
                            "msg_read": False,
                            "error": "an error occurred while updating the message state",
                        }
                    ),
                )
    else:
        return abort(
            500,
            json.dumps(
                {
                    "msg_read": False,
                    "error": "an error occurred while updating the message state",
                }
            ),
        )


@msg.route("/api/user/recipients", methods=["GET"])
def get_recipients():
    """Get all the recipients for the current user"""
    response = UserManager.get_recipients(current_user.id)
    if response.status_code == 200:
        return response.json()
    else:
        return abort(500)


#########################
#                       #
#   UTILITY FUNCTIONS   #
#                       #
#########################


def _not_valid_string(text):
    return text is None or text == "" or text.isspace()


def _get_result(json_object, page, error=False, status=200, message=""):
    """Return the result of a function (a json in test mode or a rendered template)

    :param json_object: the json to be returned in test mode
    :type json_object: json
    :param page: the name of the page to be rendered
    :type page: text
    :param error: if an error has happened in the function (default=False)
    :type error: bool
    :param status: the status code to be returned (default=200)
    :type status: int
    :param message: the message to be displayed (default="")
    :type message: text
    :returns: json in test mode or rendered template
    :rtype: json
    """
    testing = "testing" == os.getenv["FLASK_ENV"]
    if error and testing:
        abort(status, message)
    elif error:  # pragma: no cover
        return render_template(page + ".html", message=message, form=MessageForm())

    if testing:
        return json_object
    else:
        session["message"] = message
        return redirect(url_for(page, message=message, form=MessageForm()))


def _extension_allowed(filename):
    """Checks if a file is allowed to be uploaded

    :param filename: name of the file
    :type filename: str
    :returns: True if allowed, false otherwise
    :rtype: bool
    """

    # Of course, this is a toy, nothing stops you from sending an .exe as a .jpg :)
    extensions = [".jpg", ".jpeg", ".JPG", ".JPEG"]
    return any(ext in filename for ext in extensions)
