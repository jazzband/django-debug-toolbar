from debug_toolbar.toolbar import DebugToolbar

app_name = "djdt"  # See debug_toolbar/__init__.py
urlpatterns = DebugToolbar.get_urls()
