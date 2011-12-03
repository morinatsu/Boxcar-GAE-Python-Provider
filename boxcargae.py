#!/bin/python
# -*- coding:utf-8 -*-
"""
Boxcar client api for providers.
"""

## Import library functions
import urllib
import logging
from google.appengine.api import urlfetch
try:
    from hashlib import md5
except ImportError:
    from md5 import md5


## Expose the ApiClient and error classes for importing
__all__ = ["BoxcarApi", "BoxcarException"]


class BoxcarApi(object):
    """
    Boxcar Cliant API class
    """

    # The useragent to send though
    USERAGENT = "Boxcar_Client"

    # The endpoint for service
    ENDPOINT = "http://boxcar.io/devices/providers/"

    # Stores the api key
    #     @var string
    _api_key = None

    # Stores the api secret
    #     @var string
    _secret = None

    # A default icon url
    #     @var string
    _default_icon_url = ""

    def __init__(self, api_key, secret, default_icon_url):
        """
        Make a new instance of the API client

        @param api_key: your api key
        @type api_key: str
        @param secret: your api secret
        @type secret: str
        @param default_icon_url: url to a 57x57 icon to use with a message
        @type default_icon_url: str
        """
        self._api_key = api_key
        self._secret = secret
        self._default_icon_url = default_icon_url

    def invite(self, email):
        """
        Invite an existing user to add your provider

        @param email: the email address to invite
        @type email: str
        @return: bool
        """
        _result = self._http_post("notifications/subscribe",
                                {"email": email})
        if (_result.status_code == 404):
            raise BoxcarException("User not found %d" % _result.status_code)
        else:
            return self._default_response_handler(_result)

    def notify(self, email, name, message, message_id=None,
               payload=None, source_url=None, icon=None):
        """
        Send a notification

        @param email: The users MD5'd e-mail address
        @type email: str
        @param name: the name of the sender
        @type name: str
        @param message: the message body
        @type message: str
        @param message_id: an optional unique id,
                   will stop the same message getting sent twice
        @type message_id: int
        @param payload: Optional; The payload to be passed
                        in as part of the redirection URL.
                        Keep this as short as possible.
        @type payload: str
        @param source_url: Optional; This is a URL that may be used for
                       future devices. It will replace the redirect payload.
        @type source_url: str
        @param icon: Optional; This is the URL of the icon that will be shown
                     to the user. Standard size is 57x57.
        @type icon: str
        """
        return self._do_notify("notifications", email, name, message,
                               message_id, payload, source_url, icon)

    def broadcast(self, name, message, message_id=None, payload=None,
                  source_url=None, icon=None):
        """
        Send a notification to all users of your provider

        @param name: the name of the sender
        @type name: str
        @param message: the message body
        @type message: str
        @param message_id: an optional unique id,
                   will stop the same message getting sent twice
        @type message_id: int
        @param payload: Optional; The payload to be passed
                        in as part of the redirection URL.
                        Keep this as short as possible.
        @type payload: str
        @param source_url: Optional; This is a URL that may be used for
                       future devices. It will replace the redirect payload.
        @type source_url: str
        @param icon: Optional; This is the URL of the icon that will be shown
                     to the user. Standard size is 57x57.
        @type icon: str
        """
        return self._do_notify("notifications/broadcast", None, name, message,
                               message_id, payload, source_url, icon)

    def _do_notify(self, task, email, name, message, message_id=None,
                   payload=None, source_url=None, icon=None):
        """
        Internal function for actually sending the notifications

        @param task: path of task
        @type task: str
        @param name: the name of the sender
        @type name: str
        @param message: the message body
        @type message: str
        @param message_id: an optional unique id,
                   will stop the same message getting sent twice
        @type message_id: int
        @param payload: Optional; The payload to be passed
                        in as part of the redirection URL.
                        Keep this as short as possible.
        @type payload: str
        @param source_url: Optional; This is a URL that may be used for
                       future devices. It will replace the redirect payload.
        @type source_url: str
        @param icon: Optional; This is the URL of the icon that will be shown
                     to the user. Standard size is 57x57.
        @type icon: str
        """
        # if the icon was not set for this message,
        # check for the default icon and use that if set
        if ((icon is None) and (self._default_icon_url is not None)):
            icon = self._default_icon_url
        # md5 email
        if (email is not None):
            _dummy_md5 = md5()
            _md5_email = md5(email).hexdigest()
        else:
            _md5_email = None
        _notification = {
            "token": self._api_key,
            "secret": self._secret,
            "email": _md5_email,
            "notification[from_screen_name]": name,
            "notification[message]": message,
            "notification[from_remote_service_id]": message_id,
            "notification[redirect_payload]": payload,
            "notification[source_url]": source_url,
            "notification[icon_url]": icon,
        }
        # unset the null ones...
        _filtered_notification = dict()
        for (key, val) in [(key, val) \
            for (key, val) in _notification.iteritems() if val is not None]:
            _filtered_notification[key] = val
        _result = self._http_post(task, _filtered_notification)
        return self._default_response_handler(_result)

    def _default_response_handler(self, result):
        """
        Correctly handle the error / success states from the boxcar servers

        @see http://boxcar.io/help/api/providers
        @param result:
        @type result: dict
        @return str
        """
        # work out what to do based on http code
        if (result.status_code == 200):
            # return true,
            # currently there are no responses returning anything...
            return True
        elif (result.status_code == 400):
            # it is because you failed to send the proper parameters
            raise BoxcarException("Incorrect parameters passed %d" %
                                  result.status_code)
        elif (result.status_code == 401):
            # For request failures,
            # you will receive either HTTP status 403 or 401.
            # HTTP status code 401's,
            # it is because you are passing in either an invalid token,
            # or the user has not added your service.
            # Also, if you try and send the same notification id twice.
            raise BoxcarException("Request failed (Probably your fault) %d" %
                                  result.status_code)
        elif (result.status_code == 403):
            raise BoxcarException("Request failed (General) %d" %
                                  result.status_code)
        else:
            # Unkown code
            raise BoxcarException("Unknown response: %d" % result.status_code)

    def _http_post(self, task, data):
        """
        HTTP POST a specific task with the supplied data

        @param task: path of task
        @type task: str
        @param data: supplied data
        @param date: dict
        @return dict
        """
        _url = self.ENDPOINT + self._api_key + "/" + task
        _post_fields = urllib.urlencode(dict([key, val.encode("utf-8") \
            if isinstance(val, unicode) else val] \
            for (key, val) in data.iteritems()))

        _result = urlfetch.fetch(_url,
                                method="POST",
                                headers={"User-Agent": self.USERAGENT},
                                payload=_post_fields
        )
        return _result


class BoxcarException(Exception):
    """ Boxcar exception """

    def __init__(self, error_msg):
        self.msg = error_msg

    def __str__(self):
        return "Boxcar server returned error: %s" % self.msg
#
