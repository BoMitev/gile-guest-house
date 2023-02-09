from django.core.exceptions import ValidationError


def is_room_capacity_exceeded(reservation):
    if reservation.room.room_capacity < reservation.total_guests:
        raise ValidationError({"room": "* Броят на гостите надхвърля капацита на стаята.",
                               "adults": "",
                               "children": "",
                               })


def is_room_chosen(reservation):
    if reservation.confirm:
        raise ValidationError({"room": "* Изберете стая за да потвърдите резервацията."})


def validate_dates(reservation):
    if reservation.check_in.date() >= reservation.check_out.date():
        raise ValidationError({"check_in": "Датата на настаняване трябва да е преди датата на напускане.",
                               "check_out": ""})


def is_room_busy(is_room_busy):
    if is_room_busy:
        raise ValidationError({
            "room": f"* Стая {is_room_busy.room_id} е заета от {is_room_busy.check_in.date()} до {is_room_busy.check_out}",
            "check_in": "",
            "check_out": ""})


