# ==========================================================
#  DASHBOARD — No ORM, uses DB objects only
# ==========================================================
#
#  All stats come from fn_get_dashboard_stats(p_user_id, p_role)
#  which reads from mv_dashboard_stats (materialized view) for
#  admin/manager, or counts directly from delivery for other roles.

from django.db import connection
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    role = request.user.role

    # SELECT * FROM fn_get_dashboard_stats(user_id, role)
    # Returns TABLE(stat_name TEXT, stat_value BIGINT)
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM fn_get_dashboard_stats(%s, %s)",
            [request.user.id, role],
        )
        stats = {row[0]: row[1] for row in cur.fetchall()}

    return render(request, "dashboard/admin.html", {"stats": stats, "role": role})
