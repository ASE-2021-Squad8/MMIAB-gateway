from mib import app
from flask import abort
import requests
from circuitbreaker import circuit


class MessageManager:
    MESSAGE_ENDPOINT = app.config["MESSAGE_MS_URL"]
    NOTIFICATIONS_ENDPOINT = app.config["NOTIFICATIONS_MS_URL"]
    REQUESTS_TIMEOUT_SECONDS = app.config["REQUESTS_TIMEOUT_SECONDS"]

    @classmethod
    @circuit
    def get_message(cls, message_id):

        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT + "/message/" + str(message_id),
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_day_message(cls, year, month, day, user_id):
        """Get all the sent messages for a specific day"""
        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT
                + "/message/"
                + str(user_id)
                + "/sent/"
                + str(year)
                + "/"
                + str(month)
                + "/"
                + str(day),
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_sent_messages_metadata(cls, user_id):

        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT + "/message/" + str(user_id) + "/sent/metadata",
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_received_messages_metadata(cls, user_id):

        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT
                + "/message/"
                + str(user_id)
                + "/received/metadata",
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_attachment(cls, msg_id):
        """
        This method contacts the message microservice
        in order to retrieve the attachment of the message with id = msg_id.
        :param msg_id: the message id
        """
        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT + "/message/" + str(msg_id) + "/attachment",
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def send_message(cls, msg):
        """
        Send a message via the messages microservice
        """
        try:
            response = requests.post(
                cls.MESSAGE_ENDPOINT + "/message",
                json=msg,
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def delete_message_lottery_points(cls, message_id: int):
        """
        Contact the messaging microservice in order to sort out scheduled messages
        in the future using points.
        :param msg_id: the message id of the message that the user wants to delete
        """
        try:
            response = requests.delete(
                cls.MESSAGE_ENDPOINT + "/lottery/" + str(message_id),
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def update_message(cls, message_id: int, attribute: str, value):
        try:
            response = requests.put(
                cls.MESSAGE_ENDPOINT + "/message",
                json={"message_id": int(message_id), "attribute": attribute, "value": value},
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_draft(cls, draft_id: int):
        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT + "/message/draft/" + str(draft_id),
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def get_all_drafts_for_user(cls, user_id: int):
        try:
            response = requests.get(
                cls.MESSAGE_ENDPOINT + "/message/" + str(user_id) + "/draft",
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def send_notification(cls, sender: str, receiver: str):
        try:
            response = requests.put(
                cls.NOTIFICATIONS_ENDPOINT + "/email",
                json={
                    "sender": "noreply@mmiab.com",
                    "recipient": sender,
                    "body": receiver + " has just read your message",
                },
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def save_new_draft(cls, draft):
        try:
            response = requests.post(
                cls.MESSAGE_ENDPOINT + "/message/draft",
                json=draft,
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def update_draft(cls, draft_id: int, draft):
        try:
            response = requests.put(
                cls.MESSAGE_ENDPOINT + "/message/draft/" + str(draft_id),
                json=draft,
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    @circuit
    def delete_draft(cls, draft_id: int):
        try:
            response = requests.delete(
                cls.MESSAGE_ENDPOINT + "/message/draft/" + str(draft_id),
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
