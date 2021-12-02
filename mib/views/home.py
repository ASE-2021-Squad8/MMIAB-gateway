from flask import Blueprint, render_template
from mib.forms.forms import MessageForm
home = Blueprint('home', __name__)


@home.route('/', methods=['GET', 'POST'])
def index():
    """General route for the index page
    """
    form = MessageForm()
    return render_template("index.html", form=form)


@home.route('/settings', methods=['GET'])
def get_settings():  # noqa: E501
    """Render settings page
     # noqa: E501
    :rtype: None
    """
    return render_template("settings.html")

