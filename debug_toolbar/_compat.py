try:
    from django.contrib.auth.decorators import login_not_required
except ImportError:
    # For Django < 5.1, copy the current Django implementation
    def login_not_required(view_func):
        """
        Decorator for views that allows access to unauthenticated requests.
        """
        view_func.login_required = False
        return view_func
