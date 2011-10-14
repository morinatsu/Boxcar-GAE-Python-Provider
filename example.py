#!/bin/python
# -*- coding:utf-8 -*-
"""
Sample file for the boxcar GAE/Python provider client
"""

import logging
from datetime import date, datetime
from string import Template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from boxcargae import BoxcarApi


class TestBoxcar(webapp.RequestHandler):
    """test boxcar api class"""
    def get(self):
        """test boxcar api method"""
        _api_key = 'xxxxxxxxxxxxxxxxxxxx'
        _api_sec = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        _your_email = 'xxxxxxxxx@xxxxx.xxx'
        # instantiate a new instance of the boxcar api
        boxcar = BoxcarApi(_api_key,
                           _api_sec,
                           'http://xxxxx.xxxx.xx.xx.xx.xxxxxxxxx.xxx/'
                           'xxxxxxxxxx.png')
        # send a broadcast (to all your subscribers)
        template = Template('Test Broadcast, this was sent at $date')
        message = template.substitute(date=date.today())
        boxcar.broadcast('Test Name', message)
        # send a message to a specific user, with an ID of 000-999
        template = Template('Hey $email this was sent')
        message = template.substitute(email=_your_email)
        boxcar.notify(_your_email,
                      'Test name',
                      message,
                      message_id=int(datetime.now().strftime('%f')) % 1000)


logging.getLogger().setLevel(logging.DEBUG)
_APPLICATION = webapp.WSGIApplication([("/.*", TestBoxcar)],
                                      debug=True)


def real_main():
    """ main for wsgi app """
    run_wsgi_app(_APPLICATION)


if __name__ == "__main__":
    real_main()
