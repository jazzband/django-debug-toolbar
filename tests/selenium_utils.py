# coding: utf-8

from __future__ import absolute_import, unicode_literals
import os

try:
    from selenium import webdriver
except ImportError:
    webdriver = None


def create_web_driver():
    if not webdriver:
        return EnvironmentError(
            "Your environment must have selenium installed to use this.")
    username = os.environ.get("SAUCE_USERNAME")
    access_key = os.environ.get("SAUCE_ACCESS_KEY")
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    capabilities.update({
        "tunnel-identifier": os.environ.get("TRAVIS_JOB_NUMBER"),
        "build": os.environ.get("TRAVIS_BUILD_NUMBER"),
        "tags": [os.environ.get("TRAVIS_PYTHON_VERSION"), "CI"],
    })
    hub_url = "{0}:{1}@localhost:4445".format(username, access_key)
    if username:
        driver = webdriver.Remote(
            desired_capabilities=capabilities,
            command_executor="http://{0}/wd/hub".format(hub_url))
    else:
        driver = webdriver.Firefox()
    return driver
