#!/usr/bin/python3
from abc import ABC
from typing import Any

import tornado.ioloop
import tornado.web
import tornado.netutil
import tornado.httpserver
import tornado.httpclient

import os
import signal
import subprocess
from datetime import datetime
import isodate

import json

from PictureManager import PictureManager
from SpaceApiEntry import SpaceApiEntry
from SpaceStatusObserver import SpaceStatusObserver

startup_timestamp = datetime.now()

class BaseCORSHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_default_headers()
        self.set_status(204)
        self.finish()

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_default_headers()
        super().write_error(status_code, **kwargs)


class HealthHandler(tornado.web.RequestHandler, ABC):
    # noinspection PyAttributeOutsideInit
    def initialize(self):
        self.git_version = self._load_git_version()

    @staticmethod
    def _load_git_version():
        v = None

        # try file git-version.txt first
        gitversion_file = "git-version.txt"
        if os.path.exists(gitversion_file):
            with open(gitversion_file) as f:
                v = f.readline().strip()

        # if not available, try git
        if v is None:
            try:
                v = subprocess.check_output(["git", "describe", "--always", "--dirty"],
                                            cwd=os.path.dirname(__file__)).strip().decode()
            except subprocess.CalledProcessError as e:
                print("Checking git version lead to non-null return code ", e.returncode)

        return v

    def get(self):
        health = dict()
        health['api_version'] = 'v0'

        if self.git_version is not None:
            health['git_version'] = self.git_version

        health['timestamp'] = isodate.datetime_isoformat(datetime.now())
        health['uptime'] = isodate.duration_isoformat(datetime.now() - startup_timestamp)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(health, indent=4))
        self.set_status(200)


class Oas3Handler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        # This is the proposed content type,
        # but browsers like Firefox try to download instead of display the content
        # self.set_header("Content-Type", "text/vnd.yml")
        with open('OAS3.yml', 'r') as f:
            oas3 = f.read()
            self.write(oas3)
        self.finish()


class SpaceAPIHandler(tornado.web.RequestHandler, ABC):
    # noinspection PyAttributeOutsideInit
    def initialize(self, observer):
        self.observer = observer

    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self.observer.get_space_api_entry(), indent=4))
        self.finish()

class SpaceStateTextHandler(tornado.web.RequestHandler, ABC):
    # noinspection PyAttributeOutsideInit
    def initialize(self, observer):
        self.observer = observer

    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write("open" if self.observer.space_api_entry.is_open() else "closed")
        self.finish()


class PictureHandler(tornado.web.RequestHandler, ABC):
    # noinspection PyAttributeOutsideInit
    def initialize(self, picture_manager):
        self.picture_manager = picture_manager

    def get(self):
        self.set_header("Content-Type", "image/png")
        self.write(self.picture_manager.get_image())
        self.finish()


def make_app(observer, picture_manager):
    return tornado.web.Application([
        (r"/health", HealthHandler),
        (r"/oas3", Oas3Handler),
        (r"/json", SpaceAPIHandler, dict(observer=observer)),
        (r"/text", SpaceStateTextHandler, dict(observer=observer)),
        (r"/state.png", PictureHandler, dict(picture_manager=picture_manager)),
    ])


def load_env(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default


signal_received = False


def main():
    arg_port = load_env('PORT', 8080)
    arg_mqtt_broker_server = load_env('MQTT_BROKER', 'mqtt')
    arg_mqtt_broker_port = load_env('MQTT_PORT', 1883)
    arg_topic_status = load_env('MQTT_TOPIC_STATUS', 'status')
    arg_topic_lastchange = load_env('MQTT_TOPIC_LASTCHANGE', 'lastchange')

    # Setup

    observer = SpaceStatusObserver(
        broker=arg_mqtt_broker_server,
        port=arg_mqtt_broker_port,
        topic_status=arg_topic_status,
        topic_lastchange=arg_topic_lastchange,
        space_api_entry=SpaceApiEntry.create_netz39()
    )
    observer.start()

    picture_manager = PictureManager(
        is_open_func=observer.space_api_entry.is_open,
        open_image_path="../assets/open.png",
        closed_image_path="../assets/closed.png"
    )

    app = make_app(observer, picture_manager)
    sockets = tornado.netutil.bind_sockets(arg_port, '')
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)

    port = None

    for s in sockets:
        print('Listening on %s, port %d' % s.getsockname()[:2])
        if port is None:
            port = s.getsockname()[1]

    ioloop = tornado.ioloop.IOLoop.instance()

    def register_signal(sig, _frame):
        # noinspection PyGlobalUndefined
        global signal_received
        print("%s received, stopping server" % sig)
        server.stop()  # no more requests are accepted
        signal_received = True

    def stop_on_signal():
        # noinspection PyGlobalUndefined
        global signal_received
        if signal_received:
            ioloop.stop()
            print("IOLoop stopped")

    tornado.ioloop.PeriodicCallback(stop_on_signal, 1000).start()
    signal.signal(signal.SIGTERM, register_signal)
    print("Starting server")

    global signal_received
    while not signal_received:
        try:
            ioloop.start()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            register_signal(signal.SIGTERM, None)

    # Teardown

    print("Server stopped")


if __name__ == "__main__":
    main()
