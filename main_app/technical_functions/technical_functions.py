from django.db.models import Q
from datetime import timedelta


def get_all_free_rooms(check_in, check_out, reservation_id=0, **kwargs):
    check_in = check_in.replace(hour=0, minute=0)
    busy_rooms = kwargs['reservedrooms'].objects.values_list('room', flat=True).exclude(reservation__id=reservation_id)\
        .exclude(room__isnull=True).filter(
        (Q(reservation__check_in__range=(check_in, check_out)))
        | (Q(reservation__check_out__range=(check_in + timedelta(days=1), check_out)))
        | (Q(reservation__check_in__lte=check_in, reservation__check_out__gt=check_out))).distinct()
    free_rooms = kwargs['room'].objects.exclude(id__in=busy_rooms).all()
    return free_rooms