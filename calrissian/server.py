import os

from twisted.application.service import Application

from twisted.application.internet import TCPServer

from twisted.python.filepath import FilePath

from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web._responses import NOT_FOUND


DOCUMENTS = FilePath(__file__).parent().child("public")
ERROR_RESOURCE = DOCUMENTS.child("error").child("index.html")
LISTEN_ON = os.environ.get("LISTEN_ON")


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

files = File(DOCUMENTS.path)
files.childNotFound = NoResource()

slightlyBetterSite = Site(HSTSResource(files))
slightlyBetterSite.displayTracebacks = False
slightlyBetterService6 = TCPServer(
    LISTEN_ON,
    slightlyBetterSite,
    interface='::')
slightlyBetterService6.setServiceParent(application)
