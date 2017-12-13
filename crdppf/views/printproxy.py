# -*- coding: utf-8 -*-

# Copyright (c) 2011-2015, Camptocamp SA
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.

# Adapted for the specific needs of the PLR cataster project by FV-SITN

import logging

import simplejson as json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

from crdppf.views.proxy import Proxy

from crdppf.lib.cached_content import get_cached_content, get_cached_content_l10n
from crdppf.lib.content import get_content

log = logging.getLogger(__name__)


class PrintProxy(Proxy):  # pragma: no cover

    def __init__(self, request):
        Proxy.__init__(self, request)
        self.config = self.request.registry.settings

    @view_config(route_name='printproxy_report_create')
    def report_create(self):
        """ Create PDF. """

        id = self.request.matchdict.get("id")

        body = {
            "layout": "report",
            "outputFormat": "pdf",
            "attributes": {}
        }

        body["attributes"].update(get_cached_content_l10n(self.request.params.get(
            "lang",
            self.request.registry.settings["app_config"]["lang"]
        )))

        cached_content = get_cached_content(self.request)
        dynamic_content = get_content(id, self.request)

        if dynamic_content is False:
            return HTTPBadRequest(detail='Found more then one geometry')

        body["attributes"].update(cached_content)
        body["attributes"].update(dynamic_content["attributes"])

        _string = "%s/%s/report.%s" % (
            self.config['print_url'],
            "crdppf",
            "pdf"
        )

        body = json.dumps(body)

        # Specify correct content type in headers
        h = dict(self.request.headers)
        h["Content-Type"] = "application/json"

        print_result = self._proxy_response(
            _string,
            body=body,
            method='POST',
            headers=h
        )
        self.config['id'] = self.request.matchdict.get("id")
        return print_result

    @view_config(route_name='printproxy_status')
    def status(self):
        """ PDF status. """

        _string = "%s/status/%s.json" % (
            self.config['print_url'],
            self.request.matchdict.get('ref')
        )

        return self._proxy_response(
            _string,
            headers=self.request.headers
        )

    @view_config(route_name='printproxy_report_get')
    def report_get(self):
        """ Get the PDF and store a copy for archive purposes"""

        pdf = self._proxy_response(
            "%s/report/%s" % (
                self.config['print_url'],
                self.request.matchdict.get('ref')
            ),
        )
        id = self.config['id']

        try:
            archive_path = self.config['pdf_archive_path']
        except:
            archive_path = None

        if archive_path is not None:
            import os
            filename = pdf.content_disposition.split('=')[1]
            if id is not None:
                parts = filename.split('_')
                filename = str(parts[0])+id+str('_')+str(parts[1])
            with open(os.path.join(archive_path, filename), 'wb') as f:
                f.write(pdf.body)

        return pdf
