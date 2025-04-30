# middleware.py
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.shortcuts import redirect


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('user_data_submitted'):
            last_activity_str = request.session.get('last_activity')
            if last_activity_str:
                last_activity = timezone.datetime.fromisoformat(last_activity_str)
                if timezone.now() - last_activity > timedelta(seconds=300):
                    request.session.flush()
                    if request.path != reverse('session_expired'):
                        return redirect('session_expired')

            request.session['last_activity'] = str(timezone.now())

        return self.get_response(request)