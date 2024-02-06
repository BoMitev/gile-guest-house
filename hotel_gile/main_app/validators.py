from django.core.exceptions import ValidationError
from hotel_gile.main_app.models.enums import ReservationStatus


def validate_reservation(reservation):
    if reservation.check_in.date() >= reservation.check_out.date():
        raise ValidationError({"check_in": "Датата на настаняване трябва да е преди датата на напускане.",
                               "check_out": ""})

    if reservation.status == ReservationStatus.PENDING and reservation.generate_password:
        raise ValidationError({"generate_password": "Статуса трябва да бъде потвърден за да генерирате парола"})


def validate_reserved_rooms(reserved_room):
    if reserved_room.room:
        if not reserved_room.adults:
            raise ValidationError({"room": "Посочете броя на гостите.",
                                   "adults": "",
                                   "children": "",
                                   })

        if not reserved_room.is_room_free(reserved_room.reservation.id):
            raise ValidationError({
                "room": f"* Стая {reserved_room.room.id} е заета за избрания период",
                "reservation": "check_in"
            })

        if reserved_room.room.room_capacity < reserved_room.total_guests:
            raise ValidationError({"room": "* Броят на гостите надхвърля капацита на стаята.",
                                   "adults": "",
                                   "children": "",
                                   })

        reserved_room.price = reserved_room.total_price
    else:
        if reserved_room.reservation.status != ReservationStatus.PENDING:
            raise ValidationError({"room": "* Изберете стая за да потвърдите резервацията."})
        reserved_room.price = 0
