from django.core.exceptions import ValidationError


def guests_exist(reservedroom):
    if not reservedroom.adults:
        raise ValidationError({"room": "Посочете броя на гостите.",
                               "adults": "",
                               "children": "",
                               })


def is_room_capacity_exceeded(reservedroom):
    if reservedroom.room.room_capacity < reservedroom.total_guests:
        raise ValidationError({"room": "* Броят на гостите надхвърля капацита на стаята.",
                               "adults": "",
                               "children": "",
                               })


def room_is_not_chosen():
    raise ValidationError({"room": "* Изберете стая за да потвърдите резервацията."})


def validate_dates(reservation):
    if reservation.check_in.date() >= reservation.check_out.date():
        raise ValidationError({"check_in": "Датата на настаняване трябва да е преди датата на напускане.",
                               "check_out": ""})


def room_is_busy(room_id):
    raise ValidationError({
        "room": f"* Стая {room_id} е заета за избрания период",
        "reservation": "check_in"
    })


