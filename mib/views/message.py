def attachment_get(message_id):  # noqa: E501
    """Retrieves an attachment of a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: InlineResponse2002
    """
    return 'do some magic!'


def delete_received_message(message_id):  # noqa: E501
    """Delete a received message 

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_all_received_messages_metadata():  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def get_all_sent_messages_metadata():  # noqa: E501
    """Get all sent messages metadata of an user

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def get_calendar():  # noqa: E501
    """Render user's calendar

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def get_message(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    return 'do some magic!'


def mailbox():  # noqa: E501
    """Render mailboxpage

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def send_message_page():  # noqa: E501
    """Render message page

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def send_message(body):  # noqa: E501
    """Send message

     # noqa: E501

    :param body: Send a message
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Message.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_message_lottery_points(message_id):  # noqa: E501
    """Delete a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return 'do some magic!'


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
    return 'do some magic!'
