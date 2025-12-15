from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def home(request):
    context = {
        'title': 'Home - Django App',
        'welcome_message': 'Welcome to Enhanced Django App!',
        'features': [
            'Modern UI with Bootstrap',
            'Jenkins CI/CD Pipeline',
            'Docker Containerization',
            'Health Monitoring',
            'API Endpoints',
        ],
        'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, 'myapp/index.html', context)

def about(request):
    return render(request, 'myapp/about.html', {'title': 'About'})

def dashboard(request):
    dashboard_data = {
        'title': 'Dashboard',
        'stats': {
            'uptime': '99.9%',
            'users': 150,
            'requests': 12500,
            'response_time': '45ms'
        },
        'recent_activities': [
            'Deployment completed - 10 min ago',
            'Database backup - 1 hour ago',
            'Security scan - 2 hours ago',
            'Performance test - 3 hours ago'
        ]
    }
    return render(request, 'myapp/dashboard.html', dashboard_data)

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'enhanced-django-app',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'dependencies': ['Django', 'Gunicorn', 'PostgreSQL']
    })

@csrf_exempt
def api_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'received': data,
                'status': 'processed',
                'timestamp': datetime.now().isoformat()
            })
        except:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({
        'endpoint': 'api/status',
        'methods': ['GET', 'POST'],
        'description': 'API status endpoint'
    })