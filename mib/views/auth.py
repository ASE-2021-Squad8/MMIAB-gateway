from flask import Blueprint, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user
from mib.forms.forms import LoginForm
from mib.rao.user_manager import UserManager

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login(re=False):
    """Allows the user to log into the system

    Args:
        re (bool, optional): boolean value that describes whenever
        the user's session is new or needs to be reloaded. Defaults to False.

    Returns:
        Redirects the view to the personal page of the user
    """
    form = LoginForm()

    if request.method == "GET":
        return render_template("login.html", form=form)
    elif request.method == "POST":
        email, password = form.data["email"], form.data["password"]
        user = UserManager.authenticate_user(email, password)
        if user is None:
            # user is not authenticated
            return render_template(
                "login.html",
                form=form,
                error="Not authenticated. Maybe your credentials are wrong or you have been banned/unregistered",
            )
        else:
            # user is authenticated
            login_user(user)
            return redirect(url_for("home.index"))


@auth.route("/relogin")
def re_login():
    """Method that is being called after the user's session is expired."""
    return login(re=True)


@auth.route("/logout")
@login_required
def logout():
    """This method allows the users to log out of the system

    Returns:
        Redirects the view to the home page
    """
    logout_user()
    return redirect(url_for("home.index"))
