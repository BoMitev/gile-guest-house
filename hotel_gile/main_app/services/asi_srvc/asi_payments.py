from ..payments_srvc import payments_srvc, admin_log_func
import hotel_gile.main_app.models as model


def check_order_status(reservation):
    from .asi_email import send_successful_payment_email
    data = payments_srvc.check_order_status(reservation)
    order_status = data.get('orderStatus')

    if order_status in [1, 2]:
        reservation.status = model.ReservationStatus.PAID
        admin_log_func.log_change(reservation)
        send_successful_payment_email(reservation)
        return True, data
    return False, data


def generate_payment_link(reservation):
    data = payments_srvc.generate_payment_link(reservation)
    order_id = data.get('orderId')

    if order_id:
        reservation.payment_id = order_id
        reservation.payment_counter += 1
        return True, data
    return False, data.get('errorMessage')
