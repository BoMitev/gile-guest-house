from datetime import datetime
from hotel_gile.main_app.models.enums import ReservationStatus
from hotel_gile.main_app.services.google_srvcs import create_service


def event_template(reservation, rooms):
    default_time = datetime.strptime("14:00:00", '%H:%M:%S').time()
    check_in_time = ""
    if reservation.check_in.time() != default_time:
        check_in_time = f'Час на пристигане: {reservation.check_in.time()}\n'

    description = [f'{reservation.name.title()} / {reservation.phone}']

    for room in rooms:
        description.append(f'{room.title}\n'
                           f'{room.adults}+{room.clean_children()} човека\n'
                           f'{room.stay} x {room.total_price/room.stay:.2f} = {room.total_price:.2f}лв.\n')

    if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.ACCEPTED]:
        description.append(reservation.status)

    description.append(f'{check_in_time}'
                       f'{reservation.description}')

    result = {
        'summary': reservation.title,
        'description': "\n".join(description),
        'colorId': str(rooms[0].room.id),
        'start': {
            'date': f'{reservation.check_in.date()}',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'date': f'{reservation.check_out.date()}',
            'timeZone': 'Europe/Sofia',
        },
    }

    return result


def send_update_reservation(reservation, rooms):
    if reservation.status is not ReservationStatus.PENDING:
        service = create_service()
        event = event_template(reservation, rooms)
        if reservation.external_id:
            service.events().update(calendarId='primary', eventId=reservation.external_id, body=event).execute()
        else:
            response = service.events().insert(calendarId='primary', body=event).execute()
            reservation.external_id = response['id']


def delete_reservation(reservation):
    if reservation.external_id:
        try:
            service = create_service()
            service.events().delete(calendarId='primary', eventId=reservation.external_id).execute()
        except Exception as ex:
            print(ex)
        finally:
            reservation.external_id = None
