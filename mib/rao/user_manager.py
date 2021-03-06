from mib.auth.user import User
from mib import app
from flask_login import logout_user
from flask import abort
from circuitbreaker import circuit
import requests


class UserManager:
    USERS_ENDPOINT = app.config["USERS_MS_URL"]
    REQUESTS_TIMEOUT_SECONDS = app.config["REQUESTS_TIMEOUT_SECONDS"]

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/" + str(user_id),
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        json_payload = response.json()
        if response.status_code == 200:
            # user is authenticated
            return User.build_from_json(json_payload)
        else:
            raise RuntimeError(
                "Server has sent an unrecognized status code %s"
                % response.status_code
            )

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def create_user(
        cls,
        email: str,
        password: str,
        firstname: str,
        lastname: str,
        dateofbirth,
    ):
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
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
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
        url = cls.USERS_ENDPOINT + "/user/" + str(user_id)
        response = requests.put(
            url,
            json={"email": email, "password": password},
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: User updated
        """
        logout_user()
        url = cls.USERS_ENDPOINT + "/user/" + str(user_id)
        response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def authenticate_user(cls, email: str, password: str) -> User:
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        response = requests.post(
            cls.USERS_ENDPOINT + "/authenticate",
            json=payload,
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        json_response = response.json()

        if response.status_code == 400:
            # user is not authenticated
            return None
        elif response.status_code == 200:
            user = User.build_from_json(json_response["user"])
            user.authenticate()
            return user

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def change_password(cls, user_id: int, currpw: str, newpw: str, confpw: str):
        """Call users microservice to change the password for a user
        :param user_id: id of the user who wants to change the password
        :param currpw: current password of the user who wants to change their password
        :param newpw: new password chosen by the user
        :param confpw: confirmation password, used to verify that the user has entered the currpw correctly
        """
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/password/" + str(user_id),
            json={
                "currentpassword": currpw,
                "newpassword": newpw,
                "confirmpassword": confpw,
            },
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def set_content_filter(cls, id: int, filter: str):
        """Call users microservice to change the content filter for a user

        :param id: the user id
        :param filter: 0 = disable, 1 = enable
        :return: response
        """
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/content_filter/" + str(id),
            json={"filter": filter},
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def user_unregister(cls, user_id: int):
        """Call calls the users microservice in order to unsubscribe a user

        :param user_id: id associated with the user who wants to unsubscribe
        """
        response = requests.delete(
            cls.USERS_ENDPOINT + "/user/" + str(user_id),
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_users_list_public(cls):
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/list/public",
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def report(cls, email: str):
        """Report the user with an email

        :param email: the email of the reported user
        """
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/report",
            json={"useremail": email},
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def change_data_user(cls, user_id, email, firstname, lastname, dateofbirth):
        """Interacts with the microservice of the users in order to change the data of an
        already registered user

        :param user_id: id of the user who wants to change his personal data
        :param email: new user's email
        :param firstname: new user's firstname
        :param lastname: new user's lastname
        :param dateofbirth: new date of birth of the user
        """
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/data/" + str(user_id),
            json={
                "textemail": email,
                "textfirstname": firstname,
                "textlastname": lastname,
                "textbirth": dateofbirth,
            },
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_blacklist(cls, user_id: int):
        """Get blacklisted users for user_id"""
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/black_list/" + str(user_id),
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def add_to_blacklist(cls, user_id, userlist_to_add):
        """Add list of users to blacklist of user_id"""
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/black_list/" + str(user_id),
            json={"op": "add", "users": userlist_to_add},
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def remove_from_blacklist(cls, user_id, userlist_to_remove):
        """Remove list of users from blacklist of user_id"""
        response = requests.put(
            cls.USERS_ENDPOINT + "/user/black_list/" + str(user_id),
            json={"op": "delete", "users": userlist_to_remove},
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit
    def get_user_email(cls, user_id: int):
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/" + str(user_id) + "/email",
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_recipients(cls, user_id: int):
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/" + str(user_id) + "/recipients",
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_user_public(cls, user_id: int):
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/" + str(user_id) + "/public",
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response

    @classmethod
    @circuit(expected_exception=requests.RequestException)
    def get_user_by_id_json(cls, user_id: int):
        response = requests.get(
            cls.USERS_ENDPOINT + "/user/" + str(user_id),
            timeout=cls.REQUESTS_TIMEOUT_SECONDS,
        )
        return response
