from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import (login_user, login_required)

from mib.forms import UserForm
from mib.rao.user_manager import UserManager
from mib.auth.user import User

users = Blueprint('users', __name__)


@users.route('/create_user/', methods=['GET', 'POST'])
def create_user():
    """This method allows the creation of a new user into the database

    Returns:
        Redirects the user into his profile page, once he's logged in
    """
    form = UserForm()

    if form.is_submitted():
        email = form.data['email']
        password = form.data['password']
        firstname = form.data['firstname']
        lastname = form.data['lastname']
        birthdate = form.data['birthdate']
        date = birthdate.strftime('%Y-%m-%d')
        phone = form.data['phone']
        response = UserManager.create_user(
            email,
            password,
            firstname,
            lastname,
            date,
            phone
        )

        if response.status_code == 201:
            # in this case the request is ok!
            user = response.json()
            to_login = User.build_from_json(user["user"])
            login_user(to_login)
            return redirect(url_for('home.index', id=to_login.id))
        elif response.status_code == 200:
            # user already exists
            flash('User already exists!')
            return render_template('create_user.html', form=form)
        else:
            flash('Unexpected response from users microservice!')
            return render_template('create_user.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for errorMessage in errorMessages:
                flash('The field %s is incorrect: %s' % (fieldName, errorMessage))

    return render_template('create_user.html', form=form)


@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """Deletes the data of the user from the database.

    Args:
        id_ (int): takes the unique id as a parameter

    Returns:
        Redirects the view to the home page
    """

    response = UserManager.delete_user(id)
    if response.status_code != 202:
        flash("Error while deleting the user")
        return redirect(url_for('auth.profile', id=id))
        
    return redirect(url_for('home.index'))


def change_pass_user_page():  # noqa: E501
    """Render change password template

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def change_pass_user(body=None):  # noqa: E501
    """Change password for current user

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = UserPasswordBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def content_filter_page():  # noqa: E501
    """Render content filter page

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def set_content_filter(body=None):  # noqa: E501
    """Change the content filter state

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = UserContentFilterBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def create_user_page():  # noqa: E501
    """Render sign up template

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def get_black_list():  # noqa: E501
    """Render blacklist template

    Return the user's black list page # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def update_black_list(body):  # noqa: E501
    """Update the black list for a user

    Update user black list adding or removing an user # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse200
    """
    if connexion.request.is_json:
        body = UserBlacklistBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def report_page():  # noqa: E501
    """Render report page

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def report(body=None):  # noqa: E501
    """Report a user

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = UserReportBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def search_user():  # noqa: E501
    """Render the search user page

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def unregister():  # noqa: E501
    """Unregister the current_user

    Delete a user by its id # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def user_profile():  # noqa: E501
    """Render profile template of current user

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def users_list_json():  # noqa: E501
    """Return users list

     # noqa: E501


    :rtype: List[InlineResponse2001]
    """
    return 'do some magic!'


def update_user(body):  # noqa: E501
    """Updates the fields for the current user

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = UserBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def users_list():  # noqa: E501
    """Render users list template

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


