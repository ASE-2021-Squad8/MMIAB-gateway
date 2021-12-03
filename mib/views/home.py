from flask import Blueprint, render_template
from flask_login import current_user
from flask_login.utils import login_required
from mib.forms.forms import MessageForm
from mib.views.auth import check_authenticated
import json

home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def index():
    """General route for the index page"""
    form = MessageForm()
    email = getattr(current_user, "email") if hasattr(current_user, "email") else None
    return render_template("index.html", form=form, email=email)


@home.route("/settings", methods=["GET"])
@login_required
def settings():  # noqa: E501
    """Render settings page
     # noqa: E501
    :rtype: None
    """
    check_authenticated(current_user)
    return render_template("settings.html")
