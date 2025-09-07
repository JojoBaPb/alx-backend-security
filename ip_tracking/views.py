from django.http import HttpResponse
from ratelimit.decorators import ratelimit
from django.contrib.auth import authenticate, login

# Function to set rate based on user authentication status
def dynamic_rate(user):
    if user.is_authenticated:
        return '10/m'  # 10 requests per minute for logged-in users
    return '5/m'      # 5 requests per minute for anonymous users

@ratelimit(key='ip', rate=dynamic_rate, block=True)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponse("Login successful")
        else:
            return HttpResponse("Invalid credentials", status=401)
    return HttpResponse("Login page")

