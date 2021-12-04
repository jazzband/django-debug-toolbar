from debug_toolbar.toolbar import DebugToolbar

app_name = "djdt"
urlpatterns = DebugToolbar.get_urls()
