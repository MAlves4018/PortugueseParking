from django.db import connections
from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html', {})

# Create your views here.
def health_check(request):
    # Check database connections
    db_ok = all(conn.cursor().execute("SELECT 1") for conn in connections.all())

    status = db_ok
    status_code = 200 if status else 503
    return JsonResponse({"status": "ok" if status else "unhealthy"}, status=status_code)
