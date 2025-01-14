from django.shortcuts import redirect

class BlockEmployeeAdminAccessMiddleware:
    """
    Restricts non-superuser staff and regular employees from accessing the Django admin site.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Block non-superusers from accessing `/admin/`
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            return redirect('/employee/dashboard/')  # Redirect to employee dashboard
        return self.get_response(request)