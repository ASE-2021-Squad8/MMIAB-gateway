import datetime
import json

from flask import Blueprint, redirect, render_template, url_for, request, abort
from flask_login import login_user, login_required, current_user

from mib.forms import UserForm
from mib.forms.forms import BlackListForm, ChangePassForm
from mib.rao.user_manager import UserManager
from mib.auth.user import User
from mib.views.auth import check_authenticated


users = Blueprint("users", __name__)


@users.route("/create_user", methods=["GET", "POST"])
def create_user():
    """This method allows the creation of a new user into the database

    Returns:
        Redirects the user into his profile page, once he's logged in
    """
    form = UserForm()
    if request.method == "GET":
        return render_template("create_user.html", form=form)
    elif request.method == "POST":
        if form.is_submitted():
            email = form.data["email"]
            password = form.data["password"]
            firstname = form.data["firstname"]
            lastname = form.data["lastname"]
            dateofbirth = form.data["dateofbirth"]
            date = dateofbirth.strftime("%Y-%m-%d")
            # check if date of birth is valid (in the past)
            if dateofbirth is None or dateofbirth > datetime.date.today():
                return render_template(
                    "create_user.html",
                    form=form,
                    error="Date of birth cannot be empty or in the future",
                )
            response = UserManager.create_user(
                email, password, firstname, lastname, date
            )
            if response.status_code == 201:
                return redirect(url_for("auth.login"))
            elif response.status_code == 200:
                # user already exists
                return render_template(
                    "create_user.html",
                    form=form,
                    error="A user with that email already exists",
                )


# @users.route("/delete_user/<int:id>", methods=["GET", "POST"])
# @login_required
# def delete_user(id):
#     """Deletes the data of the user from the database.

#     Args:
#         id_ (int): takes the unique id as a parameter

#     Returns:
#         Redirects the view to the home page
#     """

#     response = UserManager.delete_user(id)
#     if response.status_code != 202:
#         flash("Error while deleting the user")
#         return redirect(url_for("auth.profile", id=id))

#     return redirect(url_for("home.index"))


@users.route("/password", methods=["GET", "POST"])
def change_pass_user():  # noqa: E501
    """Render change password template
     # noqa: E501
    :rtype: None
    """
    check_authenticated(current_user)

    form = ChangePassForm()
    if request.method == "GET":
        return render_template("reset_password.html", form=form)
    elif request.method == "POST":
        user_id = current_user.id
        currpw = form.currentpassword.data
        newpw = form.newpassword.data
        confpw = form.confirmationpassword.data
        response = UserManager.change_password(user_id, currpw, newpw, confpw)
        if response.status_code == 200:
            return render_template(
                "reset_password.html", form=form, success="Password updated!"
            )
        elif response.status_code == 401:
            return render_template(
                "reset_password.html", form=form, error="Wrong current password!"
            )
        elif response.status_code == 422:
            return render_template(
                "reset_password.html",
                form=form,
                error="New password and confirmation password does not match!",
            )
        elif response.status_code == 404:
            return abort(500)


@users.route("/content_filter", methods=["GET", "POST"])
def content_filter():  # noqa: E501
    """Set content filter
     # noqa: E501
    :rtype: None
    """
    check_authenticated(current_user)
    if request.method == "GET":
        return render_template("content_filter.html")
    elif request.method == "POST":
        user_id = current_user.id
        filt = request.form["filter"]
        response = UserManager.set_content_filter(user_id, filt)
        if response.status_code == 200:
            string = "enabled" if filt == "1" else "disabled"
            return render_template(
                "content_filter.html", feedback="Your content filter has been " + string
            )
        elif response.status_code == 404:
            return abort(500)


@users.route("/blacklist", methods=["GET"])
def get_black_list():  # noqa: E501
    """Render blacklist template
    Return the user's black list page # noqa: E501
    :rtype: None
    """
    current_user = UserManager.get_user_by_id(User.id)
    f = BlackListForm()

    # TODO: get black_list
    black_list = None

    return render_template(
        "black_list.html", form=f, black_list=black_list, size=len(black_list)
    )


def update_black_list(body):  # noqa: E501
    """Update the black list for a user

    Update user black list adding or removing an user # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: InlineResponse200
    """
    if connexion.request.is_json:
        body = UserBlacklistBody.from_dict(connexion.request.get_json())  # noqa: E501
    return "do some magic!"


@users.route("/report", methods=["GET", "POST"])
def report():  # noqa: E501
    """Report a user
     # noqa: E501
    :rtype: None
    """
    check_authenticated(current_user)
    if request.method == "GET":
        return render_template("report_user.html")
    elif request.method == "POST":
        reported_email = request.form["useremail"]
        if reported_email is not None and not reported_email.isspace():
            response = UserManager.report(reported_email)
            if response.status_code == 200:
                return render_template(
                    "report_user.html", reported=reported_email + " has been reported"
                )
            elif response.status_code == 404:
                return render_template(
                    "report_user.html", error=reported_email + " does not exist"
                )
        else:
            return render_template(
                "report_user.html",
                error="You have to specify an email to report a user",
            )


@users.route("/search_bar", methods=["GET"])
def search_user():  # noqa: E501
    """Render the search user page

     # noqa: E501

    :rtype: None
    """
    response = UserManager.get_users_list_public()
    users = response.json()
    return render_template("search_user.html", userslist=users)


@users.route("/user", methods=["DELETE"])
def unregister():  # noqa: E501
    """Unregister the current_user
     # noqa: E501

    :rtype: None
    """
    check_authenticated(current_user)

    user_id = current_user.id
    response = UserManager.user_unregister(user_id)
    if response == 200:
        return redirect(url_for("home.index"))
    elif response == 404:
        return abort(500)


@users.route("/user", methods=["GET"])
def user_profile():  # noqa: E501
    """Render profile template of current user
     # noqa: E501
    :rtype: None
    """
    check_authenticated(current_user)

    user = UserManager.get_user_by_id(current_user.id)
    data = user.dateofbirth
    date_of_birth = data.strftime("%a, %d %B, %Y")
    return render_template("account_data.html", user=user, date=date_of_birth)


@users.route("/user/edit_profile", methods=["GET", "POST"])
def update_user():  # noqa: E501
    """Updates the fields for the current user # noqa: E501

    :rtype: None
    """
    check_authenticated(current_user)
    form = UserForm()
    if request.method == "GET":
        user = UserManager.get_user_by_id(current_user.id)
        return render_template("edit_profile.html", form=form, user=user)
    elif request.method == "POST":
        # If some fields are blank, return an error
        if (
            request.form["textfirstname"] == ""
            or request.form["textlastname"] == ""
            or request.form["textbirth"] == ""
            or request.form["textmail"] == ""
        ):
            user = UserManager.get_user_by_id(current_user.id)
            return render_template(
                "edit_profile.html",
                form=form,
                user=user,
                error="All fields must be completed",
            )

        response = UserManager.change_data_user(
            id=current_user.id,
            email=request.form["textmail"],
            firstname=request.form["textfirstname"],
            lastname=request.form["textlastname"],
            dateofbirth=request.form["textbirth"],
        )
        if response.status_code == 200:
            return redirect(url_for("users.user_profile"))
        elif response.status_code == 404:
            return abort(500)
        elif response.status_code == 409:
            user = UserManager.get_user_by_id(current_user.id)
            return render_template(
                "edit_profile.html",
                form=form,
                user=user,
                error="That email already exists in the database",
            )


@users.route("/users", methods=["GET"])
def users_list():  # noqa: E501
    """Render users list template
     # noqa: E501
    :rtype: None
    """
    response = UserManager.get_users_list_public()
    users = response.json()
    return render_template("users.html", users=users)
