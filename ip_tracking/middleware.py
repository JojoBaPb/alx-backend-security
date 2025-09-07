from .models import RequestLog

class IPLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path

        # Save request log
        if ip:
            RequestLog.objects.create(ip_address=ip, path=path)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Get client IP address safely, accounting for proxies"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

