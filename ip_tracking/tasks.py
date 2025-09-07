from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    sensitive_paths = ["/admin/", "/login/"]

    #Detect IPs with >100 requests in the past hour
    from django.db.models import Count

    ip_counts = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(count=Count("id"))
        .filter(count__gt=100)
    )

    for entry in ip_counts:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry["ip_address"],
            reason=f"High request volume: {entry['count']} requests/hour"
        )

    #Detect IPs accessing sensitive paths
    for path in sensitive_paths:
        logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago, path=path)
        for log in logs:
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                reason=f"Accessed sensitive path: {log.path}"
            )

