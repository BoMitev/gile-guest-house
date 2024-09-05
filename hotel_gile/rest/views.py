from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from hotel_gile.main_app.models import Room, Reservation, ReservedRooms
from hotel_gile.main_app.services import asi_payments
from hotel_gile.rest.decorators import log_api_call
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class CalcRoomPrice(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.GET:
            return Response("OK", status=status.HTTP_200_OK)

        reservation_id = int(request.GET.get('reservation_id'))
        room = int(request.GET.get('room'))
        adults = int(request.GET.get('adults'))
        children = int(request.GET.get('children'))
        discount = request.GET.get('discount')
        discount = float(discount) if discount else 0
        check_in = datetime.strptime(request.GET.get('check_in'), '%d.%m.%Y')
        check_out = datetime.strptime(request.GET.get('check_out'), '%d.%m.%Y')
        total_guests = children + adults

        room_obj = Room.objects.get(id=room)
        if total_guests > room_obj.room_capacity:
            return Response({'price_per_night': 'Няма капацитет', 'total': 'Няма капацитет'}, status=status.HTTP_200_OK)

        price_per_night, total_price = ReservedRooms.calculate_price(reservation_id, check_in, check_out, room_obj,
                                                                     adults, children, discount)

        payload = {'price_per_night': f"{price_per_night:.2f} лв.",
                   'total': f"{total_price:.2f} лв."}

        return Response(data=payload, status=status.HTTP_200_OK)


class CheckRoom(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        check_in = datetime.strptime(request.GET.get('check_in'), '%d.%m.%Y')
        check_out = datetime.strptime(request.GET.get('check_out'), '%d.%m.%Y')
        reservation_id = int(request.GET.get('reservation'))

        result = {}

        all_rooms = Reservation.get_all_free_rooms(check_in, check_out, reservation_id)
        for room in all_rooms:
            result[str(room.id)] = room.title

        return Response(data=result, status=status.HTTP_200_OK)


class Payments(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    @log_api_call
    def post(self, request):
        payment_id = request.get("mdOrder", "")
        reservation = Reservation.objects.filter(payment_id=payment_id).first()

        if reservation is None:
            return Response(data={"error": f"Reservation not found with id {payment_id}"},
                            status=status.HTTP_200_OK), status.HTTP_404_NOT_FOUND

        response, data = asi_payments.check_order_status(reservation)
        if response:
            reservation.save(has_changed=True)
        return Response(data=data, status=status.HTTP_200_OK), status.HTTP_200_OK
