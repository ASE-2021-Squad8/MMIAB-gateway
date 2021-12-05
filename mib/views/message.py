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
from flask.wrappers import Response
from flask_login import login_user, login_required, current_user
from mib.forms.forms import MessageForm
from datetime import date, datetime
import os
import hashlib
import pathlib
import json

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
        data_response = {"attachement": json_obj["media"]}
        return jsonify(data_response)
    elif response.status_code == 404:
        return abort(500)

msg.route("/message/bin/<message_id>",methods=['DELETE'])
@login_required
def delete_received_message(message_id):  # noqa: E501
    """Delete a received message
     # noqa: E501
    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    user_id=current_user.id
    response = MessageManager.set_message_is_delete(message_id, user_id)
    if response.status_code==200:
        return jsonify({"message_id": message_id})
    elif response.status_code==400:
        return _get_result(None, ERROR_PAGE, True, 404, "Wrong message id")
    elif response.status_code==404:
        return _get_result(None, ERROR_PAGE, True, 404, "User not found")



@msg.route("/message/received/metadata")
def get_all_received_messages_metadata():  # noqa: E501
    """Get all receied messages metadata of an user
     # noqa: E501
    :rtype: List[MessageMetadata]
    """
    user_id = current_user.id
    response = MessageManager.get_received_messages_metadata(user_id)
    if response.status_code==200:
        return jsonify(response)
    if response.status_code==404:
        return abort("An error occured during retrieving the metadata")
   


@msg.route("/sent/metadata", methods=["GET"])
@login_required
def get_all_sent_messages_metadata():  # noqa: E501
    """Get all sent messages metadata of an user
     # noqa: E501
    :rtype: List[MessageMetadata]
    """
    user_id = current_user.id
    response = MessageManager.get_sent_messages_metadata(user_id)
    if response.status_code==200:
        return  jsonify(response)
    if response.status_code==404:
        return abort("An error occured during retrieving the metadata")
    


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
    return jsonify(response)


@msg.route("/mailbox", methods=["GET"])
@login_required
def mailbox():  # noqa: E501
    """Render mailboxpage
     # noqa: E501
    :rtype: None
    """
    return render_template("mailbox.html")


@msg.route("/message", methods=["GET, POST"])
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
            try:
                # attempt to retrieve the draft, if present
                msg = MessageManager.unmark_draft(
                    current_user.id,
                    int(
                        -1
                        if _not_valid_string(request.form["draft_id"])
                        else request.form["draft_id"]
                    ),
                )
            except KeyError:
                # otherwise build the message from scratch
                msg = dict()
                msg["is_draft"] = False
                msg["is_delivered"] = False
                msg["is_read"] = False

            msg["delivery_date"] = delivery_date
            msg["text"] = request.form["text"]
            msg["sender"] = int(current_user.id)
            msg["recipient"] = int(recipient)

            if "attachment" in request.files and not _not_valid_string(
                request.files["attachment"].filename
            ):
                file = request.files["attachment"]

                if _extension_allowed(file.filename):
                    filename = _generate_filename(file)

                    # if the draft already has a file, delete it
                    if msg.media is not None and msg.media != "":
                        try:  # pragma: no cover
                            # unlikely to ever happen, don't include in coverage
                            os.unlink(
                                os.path.join(os.getenv["UPLOAD_FOLDER"], msg.media)
                            )
                        except:
                            # if we failed to delete the file from the disk then something is wrong
                            return _get_result(
                                None, ERROR_PAGE, True, 500, "Internal server error"
                            )

                    file.save(os.path.join(os.getenv["UPLOAD_FOLDER"], filename))
                    msg.media = filename
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


def _not_valid_string(text):
    return text is None or text == "" or text.isspace()


@msg.routes("/lottery/<message_id>")
def delete_message_lottery_points(message_id):  # noqa: E501
    """Delete a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    response = MessageManager.delete_message_lottery_points(message_id)
    
    if response.status_code == 200:
        return jsonify({
            "message_id": message_id
        })
    elif response.status_code == 400:
        return jsonify({
            "message_id": -1
        })
    elif response.status_code == 401:
        return jsonify({
            "message_id": -1
        })
    elif response.status_code == 404:
        return jsonify({
            "message_id": -1
        })


@msg.routes("/message/sent/<year>/<month>/<day>")
@login_required
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

    if day > 31 or month + 1 > 12:
        return _get_result(None, ERROR_PAGE, True, 404, "Invalid date")
    else:
        user_id=current_user.id
        messages = MessageManager.get_day_message(year,month,day,user_id)
        return jsonify(messages)


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
    return pathlib.Path(filename).suffix.lower() in {
        ".jpg",
        ".jpeg",
        ".JPG",
        ".JPEG",
    }


def _generate_filename(file):
    """Generates a filename for an uploaded file

    :param file: file handle
    :type file: file
    :returns: a filename suited for storage
    :rtype: str
    """

    # To avoid clashes, generate a filename by hashing
    # the file's contents, the sender and the time
    sha256 = hashlib.sha256()
    while True:
        # Read in chunks of 64kb to contain memory usage
        data = file.read(65536)
        if not data:
            break
        sha256.update(data)
    sha256.update(getattr(current_user, "email").encode("utf-8"))
    sha256.update(str(int(time.time())).encode("utf-8"))

    # Seek back to the origin of the file (otherwise save will fail)
    file.seek(0)

    return sha256.hexdigest() + pathlib.Path(file.filename).suffix.lower()
