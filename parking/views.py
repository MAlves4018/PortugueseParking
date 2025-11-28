from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from parking.services import SlotService


@staff_member_required
def stats_overview(request):
    """
    Simple admin statistics dashboard:
    - current occupancy snapshot
    - last 24h usage summary
    """
    service = SlotService()

    now = timezone.now()
    occupancy = service.get_current_occupancy(at=now)
    summary = service.get_usage_summary(
        period=(now - timezone.timedelta(hours=24), now)
    )

    context = {
        "now": now,
        "occupancy": occupancy,
        "summary": summary,
    }
    return render(request, "parking/stats_overview.html", context)
