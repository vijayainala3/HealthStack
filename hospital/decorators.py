# hospital/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps # Import wraps

def admin_required(function=None, redirect_url='home'):
    """
    Decorator for views that checks that the user is logged in and is an admin.
    Redirects to the specified URL (default is 'home') if not.
    """
    def _dec(view_func):
        @wraps(view_func) # Use wraps here
        def _wrapper_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Redirect to login if not logged in
                # Consider adding the 'next' parameter here if needed
                # from django.contrib.auth.views import redirect_to_login
                # return redirect_to_login(request.get_full_path(), 'login') 
                return redirect('login') 
            if request.user.role != 'ADMIN':
                # Show error and redirect if authenticated but not admin
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            # If all checks pass, run the original view function
            return view_func(request, *args, **kwargs)
        return _wrapper_view

    if function:
        return _dec(function)
    return _dec
