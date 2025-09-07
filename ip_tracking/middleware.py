from django.core.cache import cache
from .models import RequestLog
import requests

class IPLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = "YOUR_IPGEOLOCATION_API_KEY"

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        country, city = self.get_geolocation(ip)

        # Save request log
        RequestLog.objects.create(ip_address=ip, path=path, country=country, city=city)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def get_geolocation(self, ip):
        if not ip:
            return None, None

        # Check cache first (24 hours = 86400 seconds)
        cache_key = f"geo_{ip}"
        cached = cache.get(cache_key)
        if cached:
            return cached.get("country"), cached.get("city")

        # Call IP geolocation API
        try:
            url = f"https://api.ipgeolocation.io/ipgeo?apiKey={self.api_key}&ip={ip}"
            response = requests.get(url, timeout=5)
            data = response.json()
            country = data.get("country_name")
            city = data.get("city")
            # Cache result for 24 hours
            cache.set(cache_key, {"country": country, "city": city}, 86400)
            return country, city
        except Exception:
            return None, None

