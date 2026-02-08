from django.db import connection
from django.shortcuts import render
from django.http import Http404


def _dictfetchall(cursor):
    """
    Convert a cursor result into a list of dicts.
    """
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def delivery_tracking(request, tracking_number: str):
    """
    Shows the tracking timeline for a delivery.

    Preferred SQL source:
      - fn_get_delivery_tracking(tracking_number)
    Fallback:
      - v_delivery_tracking filtered by tracking_number
    """

    # ---- Option A: Use the FUNCTION (recommended) ----
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM fn_get_delivery_tracking(%s);",
            [tracking_number],
        )
        events = _dictfetchall(cursor)

    # If function returned nothing, try the VIEW as fallback
    if not events:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM v_delivery_tracking
                WHERE tracking_number = %s
                ORDER BY event_timestamp ASC;
                """,
                [tracking_number],
            )
            events = _dictfetchall(cursor)

    if not events:
        raise Http404(f"No tracking found for: {tracking_number}")

    # Handy header info (same across all rows)
    header = {
        "tracking_number": events[0].get("tracking_number"),
        "delivery_id": events[0].get("delivery_id") or events[0].get("del_id"),
    }

    return render(
        request,
        "deliveries/tracking.html",
        {
            "header": header,
            "events": events,
        },
    )
