import os

from twisted.application.service import Application

from twisted.application.internet import (
    TCPServer,
    SSLServer
)

from twisted.python.filepath import FilePath

from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web._responses import NOT_FOUND
from twisted.web.util import redirectTo

import pem

# the actual html/css/js... files being served are all located here
DOCUMENTS = FilePath(__file__).parent().child("public")
ERROR_RESOURCE = DOCUMENTS.child("error").child("index.html")

SECURE_PORT = 443
PRIVATE_KEY = FilePath(os.environ.get("PRIVATE_KEY")).path
CERTIFICATE_CHAIN = FilePath(os.environ.get("CERTIFICATE_CHAIN")).path
DH_PARAMETER = FilePath.Path(os.environ.get("DH_PARAMETER"))

dhParamPath = FilePath(DH_PARAMETER)
ctxFactory = pem.certificateOptionsFromFiles(
    PRIVATE_KEY,
    CERTIFICATE_CHAIN,
    dhParameters=pem.DiffieHellmanParameters.fromFile(dhParamPath)
)


class RedirectResource(Resource):
    isLeaf = True

    def render(self, request):
        host = request.requestHeaders.getRawHeaders('host')[0].split(':', 1)[0]
        port = ''
        if SECURE_PORT is not None:
            port = ':{0}'.format(SECURE_PORT)
        return redirectTo(
            'https://{0}{1}{2}'.format(host, port, request.uri),
            request
        )


class HSTSResource(Resource):

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def getChildWithDefault(self, name, request):
        request.responseHeaders.addRawHeader(
            'Strict-Transport-Security',
            'max-age=31536000; includeSubDomains'
        )
        return self._wrapped.getChildWithDefault(name, request)


class ErrorResource(Resource):
    """
    Return a custom 404 page
    """
    def __init__(self, status):
        Resource.__init__(self)
        self.status = status
        self.page = self._readTemplate()

    def _readTemplate(self):
        with open(ERROR_RESOURCE.path, 'r') as f:
            return f.read()

    def render(self, request):
        request.setResponseCode(self.status)
        request.setHeader(b"content-type", b"text/html; charset=utf-8")
        return self.page

    def getChild(self, chnam, request):
        return self


class NoResource(ErrorResource):
    def __init__(self):
        ErrorResource.__init__(self, NOT_FOUND)


application = Application("static-server")

plainSite = Site(RedirectResource())
plainSite.displayTracebacks = False
plainService6 = TCPServer(80, plainSite, interface='::')
plainService6.setServiceParent(application)

files = File(DOCUMENTS.path)
files.childNotFound = NoResource()

secureSite = Site(HSTSResource(files))
secureSite.displayTracebacks = False
secureService6 = SSLServer(SECURE_PORT,
                           secureSite,
                           ctxFactory,
                           interface='::')

secureService6.setServiceParent(application)
