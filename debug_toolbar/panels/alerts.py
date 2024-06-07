from html.parser import HTMLParser

from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel


class FormParser(HTMLParser):
    """
    HTML form parser, used to check for invalid configurations of forms that
    take file inputs.
    """

    def __init__(self):
        super().__init__()
        self.in_form = False
        self.current_form = {}
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.in_form = True
            self.current_form = {
                "file_form": False,
                "form_attrs": attrs,
                "submit_element_attrs": [],
            }
        elif self.in_form and tag == "input" and attrs.get("type") == "file":
            self.current_form["file_form"] = True
        elif self.in_form and (
            (tag == "input" and attrs.get("type") in {"submit", "image"})
            or tag == "button"
        ):
            self.current_form["submit_element_attrs"].append(attrs)

    def handle_endtag(self, tag):
        if tag == "form" and self.in_form:
            self.forms.append(self.current_form)
            self.in_form = False


class AlertsPanel(Panel):
    """
    A panel to alert users to issues.
    """

    title = _("Alerts")

    template = "debug_toolbar/panels/alerts.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.issues = []

    @property
    def nav_subtitle(self):
        if self.issues:
            issue_text = "issue" if len(self.issues) == 1 else "issues"
            return f"{len(self.issues)} {issue_text} found"
        else:
            return ""

    def add_issue(self, issue):
        self.issues.append(issue)

    def check_invalid_file_form_configuration(self, html_content):
        parser = FormParser()
        parser.feed(html_content)

        for form in parser.forms:
            if (
                form["file_form"]
                and form["form_attrs"].get("enctype") != "multipart/form-data"
                and not any(
                    elem.get("formenctype") == "multipart/form-data"
                    for elem in form["submit_element_attrs"]
                )
            ):
                form_id = form["form_attrs"].get("id", "no form id")
                issue = (
                    f'Form with id "{form_id}" contains file input but '
                    "does not have multipart/form-data encoding."
                )
                self.add_issue({"issue": issue})
        return self.issues

    def generate_stats(self, request, response):
        html_content = response.content.decode(response.charset)
        self.check_invalid_file_form_configuration(html_content)

        # Further issue checks can go here

        # Write all issues to record_stats
        self.record_stats({"issues": self.issues})
