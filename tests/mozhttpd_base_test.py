#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import tempfile
import unittest

import mozfile
import mozhttpd
import mozlog

from mozdownload.utils import urljoin

WDIR = 'data'
HERE = os.path.dirname(os.path.abspath(__file__))


SHORT_CHANGESET_MAPPING = {
    "a7d50e410ced": "a7d50e410ced2f0335bab09c7cc65ff2d2733b97",
}

@mozhttpd.handlers.json_response
def resource_get(request, path):
    changeset = request.query.split("=")[1]

    # TODO(ER): Create a better response, this is good enough for now
    return (200, {
      "1234": {
        "changesets": [ SHORT_CHANGESET_MAPPING.get(changeset, changeset), "..." ],
        "date": 1422654729,
        "user": "erahm@mozilla.com"
        }
      })


class MozHttpdBaseTest(unittest.TestCase):
    """Generic test class that uses a mozhttpd server"""

    def setUp(self):
        """Starts server that lists all files in the directory"""
        self.logger = mozlog.unstructured.getLogger(self.__class__.__name__)
        self.logger.setLevel('ERROR')
        self.httpd = mozhttpd.MozHttpd(port=8080, docroot=HERE,
                                       urlhandlers=[{'method': 'GET',
                                                     'path': '/hg/(.+)/json-pushes?',
                                                     'function': resource_get}])
        self.logger.debug("Serving '%s' at %s:%s" % (self.httpd.docroot,
                                                     self.httpd.host,
                                                     self.httpd.port))
        self.httpd.start(block=False)
        self.server_address = "http://%s:%s" % (self.httpd.host,
                                                self.httpd.port)
        self.wdir = urljoin(self.server_address, WDIR)
        self.hgdir = urljoin(self.server_address, "hg")

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.httpd.stop()
        mozfile.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
