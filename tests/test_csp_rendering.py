from typing import Dict
from xml.etree.ElementTree import Element

from django.conf import settings
from django.http.response import HttpResponse
from django.test.utils import ContextList, override_settings
from html5lib.constants import E
from html5lib.html5parser import HTMLParser

from .base import BaseTestCase


def _get_ns(element: Element) -> Dict[str, str]:
    """
    Return the default `xmlns`. See
    https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
    """
    if not element.tag.startswith("{"):
        return {}
    return {"": element.tag[1:].split("}", maxsplit=1)[0]}


class CspRenderingTestCase(BaseTestCase):
    "Testing if `csp-nonce` renders."

    panel_id = "StaticFilesPanel"

    def _fail_if_missing(
        self, root: Element, path: str, namespaces: Dict[str, str], nonce: str
    ):
        """
        Search elements, fail if a `nonce` attribute is missing on them.
        """
        elements = root.findall(path=path, namespaces=namespaces)
        for item in elements:
            if item.attrib.get("nonce") != nonce:
                raise self.failureException(f"{item} has no nonce attribute.")

    def _fail_if_found(self, root: Element, path: str, namespaces: Dict[str, str]):
        """
        Search elements, fail if a `nonce` attribute is found on them.
        """
        elements = root.findall(path=path, namespaces=namespaces)
        for item in elements:
            if "nonce" in item.attrib:
                raise self.failureException(f"{item} has no nonce attribute.")

    def _fail_on_invalid_html(self, content: bytes, parser: HTMLParser):
        "Fail if the passed HTML is invalid."
        if parser.errors:
            default_msg = ["Content is invalid HTML:"]
            lines = content.split(b"\n")
            for position, errorcode, datavars in parser.errors:
                default_msg.append("  %s" % E[errorcode] % datavars)
                default_msg.append("    %r" % lines[position[0] - 1])
            msg = self._formatMessage(None, "\n".join(default_msg))
            raise self.failureException(msg)

    @override_settings(
        DEBUG=True, MIDDLEWARE=settings.MIDDLEWARE + ["csp.middleware.CSPMiddleware"]
    )
    def test_exists(self):
        "A `nonce` should exists when using the `CSPMiddleware`."
        response = self.client.get(path="/regular/basic/")
        if not isinstance(response, HttpResponse):
            raise self.failureException(f"{response!r} is not a HttpResponse")
        self.assertEqual(response.status_code, 200)
        parser = HTMLParser()
        el_htmlroot: Element = parser.parse(stream=response.content)
        self._fail_on_invalid_html(content=response.content, parser=parser)
        self.assertContains(response, "djDebug")
        namespaces = _get_ns(element=el_htmlroot)
        context: ContextList = response.context  # pyright: ignore[reportAttributeAccessIssue]
        nonce = str(context["toolbar"].request.csp_nonce)
        self._fail_if_missing(
            root=el_htmlroot, path=".//link", namespaces=namespaces, nonce=nonce
        )
        self._fail_if_missing(
            root=el_htmlroot, path=".//script", namespaces=namespaces, nonce=nonce
        )

    @override_settings(DEBUG=True)
    def test_missing(self):
        "A `nonce` should not exist when not using the `CSPMiddleware`."
        response = self.client.get(path="/regular/basic/")
        if not isinstance(response, HttpResponse):
            raise self.failureException(f"{response!r} is not a HttpResponse")
        self.assertEqual(response.status_code, 200)
        parser = HTMLParser()
        el_htmlroot: Element = parser.parse(stream=response.content)
        self._fail_on_invalid_html(content=response.content, parser=parser)
        self.assertContains(response, "djDebug")
        namespaces = _get_ns(element=el_htmlroot)
        self._fail_if_found(root=el_htmlroot, path=".//link", namespaces=namespaces)
        self._fail_if_found(root=el_htmlroot, path=".//script", namespaces=namespaces)
