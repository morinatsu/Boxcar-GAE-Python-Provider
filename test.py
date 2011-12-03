#!/bin/python
# -*- coding:utf-8 -*-
"""
unit test for boxcargae
"""

import unittest
from minimock import mock, restore, Mock, TraceTracker, assert_same_trace
import google.appengine.api
import boxcargae


class Response(object):
    """ responce of urlfetch """
    def __init__(self, code, *args, **kw):
        """ make dummy responce """
        self.status_code = code


class TestBoxcarGAE(unittest.TestCase):
    """ test BoxcarGAE """
    def setUp(self):
        # create new instance
        self.boxcar = boxcargae.BoxcarApi('xxxxxxxxxxxxxxxxxxxx',
                           'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                           'xxxxxxxxx@xxxxx.xxx')

    def tearDown(self):
        restore()


class TestiBoxcarGAENormal(TestBoxcarGAE):
    """ normal cases class """
    def test_invite(self):
        # mock urlfetch
        trace = TraceTracker()
        response = Response(200) 
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # invite
        self.boxcar.invite('zzzzzzzz@zzzz.zzzz')
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications/subscribe',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='email=zzzzzzzz%40zzzz.zzzz')\n")

    def test_broadcast(self):
        # mock urlfetch
        trace = TraceTracker()
        response = Response(200) 
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # send a broadcast                   
        self.boxcar.broadcast('test_normal', 'broadcast message')
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications/broadcast',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=broadcast+message&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bfrom_screen_name%5D=test_normal')\n")

    def test_notify(self):
        # mock urlfetch
        trace = TraceTracker()
        response = Response(200) 
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # send a notification
        self.boxcar.notify('yyyyyyyy@yyyyy.yyy',
                           'test_normal',
                           'notification message',
                            message_id=200)
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='notification%5Bfrom_remote_service_id%5D=200&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=notification+message&"
                         "email=fd2504c1a700746932666efec57e4b92&"
                         "notification%5Bfrom_screen_name%5D=test_normal')\n")


class TestiBoxcarGAEError(TestBoxcarGAE):
    """ error cases class """
    def test_invite(self):
        """ error cases class """
        # mock urlfetch
        response = Response(404) 
        trace = TraceTracker()
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # user not found(404)
        self.assertRaises(boxcargae.BoxcarException, 
                          self.boxcar.invite, 'yyyyyyy@zzzz.zzzz')
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications/subscribe',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='email=yyyyyyy%40zzzz.zzzz')\n")

    def test_incorrect_parameter(self):
        # mock urlfetch
        response = Response(400) 
        trace = TraceTracker()
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # incorrect parameter(400)
        self.assertRaises(boxcargae.BoxcarException, 
                          self.boxcar.notify, 'yyyyyyyy@yyyyy.yyy',
                                              'test_error',
                                              'notification error',
                                              message_id=400)
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='notification%5Bfrom_remote_service_id%5D=400&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=notification+error&"
                         "email=fd2504c1a700746932666efec57e4b92&"
                         "notification%5Bfrom_screen_name%5D=test_error')\n")

    def test_request_failure(self):
        # mock urlfetch
        response = Response(401) 
        trace = TraceTracker()
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # request failure(401)
        self.assertRaises(boxcargae.BoxcarException, 
                          self.boxcar.notify, 'yyyyyyyy@yyyyy.yyy',
                                              'test_error',
                                              'notification error',
                                              message_id=401)
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='notification%5Bfrom_remote_service_id%5D=401&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=notification+error&"
                         "email=fd2504c1a700746932666efec57e4b92&"
                         "notification%5Bfrom_screen_name%5D=test_error')\n")

    def test_request_failure_403(self):
        # mock urlfetch
        response = Response(403) 
        trace = TraceTracker()
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # request failure(403)
        self.assertRaises(boxcargae.BoxcarException, 
                          self.boxcar.notify, 'yyyyyyyy@yyyyy.yyy',
                                              'test_error',
                                              'notification error',
                                              message_id=403)
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='notification%5Bfrom_remote_service_id%5D=403&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=notification+error&"
                         "email=fd2504c1a700746932666efec57e4b92&"
                         "notification%5Bfrom_screen_name%5D=test_error')\n")

    def test_unknown_error(self):
        # mock urlfetch
        response = Response(500) 
        trace = TraceTracker()
        boxcargae.urlfetch = Mock('boxcargae.urlfetch')
        boxcargae.urlfetch.fetch = Mock('fetch',
                                        returns=response, 
                                        tracker=trace)
        # unknown error(500)
        self.assertRaises(boxcargae.BoxcarException, 
                          self.boxcar.notify, 'yyyyyyyy@yyyyy.yyy',
                                              'test_error',
                                              'unknown error',
                                              message_id=500)
        assert_same_trace(trace,
            "Called fetch(\n"
            "    'http://boxcar.io/devices/providers/xxxxxxxxxxxxxxxxxxxx/notifications',\n"
            "    headers={'User-Agent': 'Boxcar_Client'},\n"
            "    method='POST',\n"
            "    payload='notification%5Bfrom_remote_service_id%5D=500&"
                         "notification%5Bicon_url%5D=xxxxxxxxx%40xxxxx.xxx&"
                         "secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&"
                         "token=xxxxxxxxxxxxxxxxxxxx&"
                         "notification%5Bmessage%5D=unknown+error&"
                         "email=fd2504c1a700746932666efec57e4b92&"
                         "notification%5Bfrom_screen_name%5D=test_error')\n")


if __name__ == '__main__':
    unittest.main()
