from mib.auth.user import User
from mib import app
from flask_login import logout_user
from flask import abort
import requests


class UserManager:
    USERS_ENDPOINT = app.config["USERS_MS_URL"]
    REQUESTS_TIMEOUT_SECONDS = app.config["REQUESTS_TIMEOUT_SECONDS"]

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get(
                cls.USERS_ENDPOINT + "/user/" + str(user_id) + "/public",
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            json_payload = response.json()
            if response.status_code == 200:
                # user is authenticated
                user = response
            else:
                raise RuntimeError(
                    "Server has sent an unrecognized status code %s"
                    % response.status_code
                )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    # @classmethod
    # def get_user_by_email(cls, user_email: str):
    #     """
    #     This method contacts the users microservice
    #     and retrieves the user object by user email.
    #     :param user_email: the user email
    #     :return: User obj with email=user_email
    #     """
    #     try:
    #         response = requests.get(
    #             cls.USERS_ENDPOINT + "/user_email/" + user_email,
    #             timeout=cls.REQUESTS_TIMEOUT_SECONDS,
    #         )
    #         json_payload = response.json()
    #         user = None

    #         if response.status_code == 200:
    #             user = User.build_from_json(json_payload)
    #         else response.status_code == 404:
    #             return {"message": }

    #     except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    #         return abort(500)

    #     return user

    @classmethod
    def create_user(
        cls,
        email: str,
        password: str,
        firstname: str,
        lastname: str,
        dateofbirth,
    ):
        try:
            response = requests.post(
                cls.USERS_ENDPOINT + "/user",
                json={
                    "email": email,
                    "password": password,
                    "firstname": firstname,
                    "lastname": lastname,
                    "dateofbirth": dateofbirth,
                },
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def update_user(cls, user_id: int, email: str, password: str):
        """
        This method contacts the users microservice
        to allow the users to update their profiles
        :param password:
        :param email:
        :param user_id: the customer id
            email: the user email
            password: the user password
        :return: User updated
        """
        try:
            url = cls.USERS_ENDPOINT + "/user/" + str(user_id)
            response = requests.put(
                url,
                json={"email": email, "password": password},
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: User updated
        """
        try:
            logout_user()
            url = cls.USERS_ENDPOINT + "/user/" + str(user_id)
            response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> User:
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        try:
            print("trying response....")
            response = requests.post(
                cls.USERS_ENDPOINT + "/authenticate",
                json=payload,
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            print("received response....")
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        if response.status_code == 401:
            # user is not authenticated
            return None
        elif response.status_code == 200:
            user = User.build_from_json(json_response["user"])
            return user
        else:
            raise RuntimeError(
                "Microservice users returned an invalid status code %s, and message %s"
                % (response.status_code, json_response["error_message"])
            )
       
    @classmethod
    def change_password(cls, user_id: int, currpw: str, newpw: str, confpw: str):
        """Call users microservice to change the password for a user
        :param user_id: id of the user who wants to change the password
        :param currpw: current password of the user who wants to change their password
        :param newpw: new password chosen by the user
        :param confpw: confirmation password, used to verify that the user has entered the currpw correctly
        """
        try:
            url = cls.USERS_ENDPOINT + "/user/password/" + str(user_id),
            response = requests.put(
                url,
                json={"currentpassword": currpw, "newpassword": newpw, "confirmpassword": confpw},
                timeout=cls.REQUESTS_TIMEOUT_SECONDS,
            )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def set_content_filter(cls, id: int, filter: int):
        """Call users microservice to change the content filter for a user

        :param id: the user id
        :param filter: 0 = disable, 1 = enable
        :return: response
        """
        try:
            response = requests.put(
                cls.USERS_ENDPOINT + "/user/content_filter/" + str(id),
                json={"filter": filter},
                timeout=cls.REQUESTS_TIMEOUT_SECONDS
            )
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)
