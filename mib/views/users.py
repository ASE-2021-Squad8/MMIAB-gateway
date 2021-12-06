import datetime
import json

from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    abort,
    make_response,
    jsonify,
)
from flask.wrappers import Response
from flask_login import logout_user, login_required, current_user

from mib.forms import UserForm
from mib.forms.forms import BlackListForm, ChangePassForm
from mib.rao.user_manager import UserManager


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


@users.route("/password", methods=["GET", "POST"])
@login_required
def change_pass_user():  # noqa: E501
    """Render change password template
     # noqa: E501
    :rtype: None
    """

    form = ChangePassForm()
    if request.method == "GET":
        return render_template("reset_password.html", form=form)
    elif request.method == "POST":
        user_id = current_user.id
        currpw = form.currentpassword.data
        newpw = form.newpassword.data
        confpw = form.confirmpassword.data
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
                error="New password and confirmation password do not match!",
            )
        elif response.status_code == 404:
            return abort(500)


@users.route("/content_filter", methods=["GET", "POST"])
@login_required
def content_filter():  # noqa: E501
    """Set content filter
     # noqa: E501
    :rtype: None
    """
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


@users.route("/blacklist", methods=["GET", "POST"])
@login_required
def black_list():  # noqa: E501
    """Render blacklist template
    Return the user's black list page # noqa: E501
    :rtype: None
    """
    if request.method == "GET":
        response = UserManager.get_blacklist(current_user.id)
        if response.status_code == 200:
            users = response.json()
            blacklisted = users["blacklisted"]
            candidates = users["candidates"]
        else:
            return abort(500)

        f = BlackListForm()
        f.users.choices = [(u["id"], u["email"]) for u in candidates]
        f.black_users.choices = [(u["id"], u["email"]) for u in blacklisted]

        return render_template("black_list.html", form=f, size=len(blacklisted))
    elif request.method == "POST":
        user_id = current_user.id
        result = False
        json_data = json.loads(request.data)
        members_id = json_data["users"]
        users = [dict(id=int(i)) for i in members_id]

        if json_data["op"] == "delete":
            result = UserManager.remove_from_blacklist(user_id, users)
        elif json_data["op"] == "add":
            result = UserManager.add_to_blacklist(user_id, users)

        response = UserManager.get_blacklist(user_id)
        if response.status_code == 200:
            users = response.json()
            blacklisted = users["blacklisted"]
            candidates = users["candidates"]
        else:
            return abort(500)
        body = dict()
        body.update({"users": candidates})
        body.update({"black_users": blacklisted})
        return make_response(jsonify(body), 200 if result else 500)


@users.route("/report", methods=["GET", "POST"])
@login_required
def report():  # noqa: E501
    """Report a user
     # noqa: E501
    :rtype: None
    """
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


@users.route("/unregister", methods=["GET"])
@login_required
def unregister():  # noqa: E501
    """Unregister the current_user
     # noqa: E501

    :rtype: None
    """
    user_id = current_user.id
    response = UserManager.user_unregister(user_id)
    if response.status_code == 200:
        logout_user()
        return redirect(url_for("home.index"))
    elif response.status_code == 404:
        return abort(500)


@users.route("/user", methods=["GET"])
@login_required
def user_profile():  # noqa: E501
    """Render profile template of current user
     # noqa: E501
    :rtype: None
    """
    user = UserManager.get_user_by_id(current_user.id)
    data = user.dateofbirth
    return render_template("account_data.html", user=user, date=data)


@users.route("/user/edit_profile", methods=["GET", "POST"])
@login_required
def update_user():  # noqa: E501
    """Updates the fields for the current user # noqa: E501

    :rtype: None
    """
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
            or request.form["textemail"] == ""
            or datetime.datetime.strptime(request.form["textbirth"], "%Y-%m-%d")
            > datetime.datetime.today()
        ):
            user = UserManager.get_user_by_id(current_user.id)
            return render_template(
                "edit_profile.html",
                form=form,
                user=user,
                error="All fields must be completed and the date must be in the past",
            )

        response = UserManager.change_data_user(
            user_id=current_user.id,
            email=request.form["textemail"],
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


@users.route("/api/user/recipients", methods=["GET"])
def get_recipients():
    """Get all the recipients for the current user"""
    response = UserManager.get_recipients(current_user.id)
    if response.status_code == 200:
        return json.dumps(response.json())
    else:
        return abort(500)


@users.route("/api/user/<id>/public", methods=["GET"])
def get_user_public(id):
    response = UserManager.get_user_public(id)
    if response.status_code == 200:
        return json.dumps(response.json())
    else:
        return abort(500)
