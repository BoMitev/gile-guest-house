def get_content_type_for_model(obj):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def log_change(obj):
    from django.contrib.admin.models import CHANGE, LogEntry
    from django.contrib.auth.models import User

    user = User.objects.filter(username="dsk_payment_srvc").first()

    return LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message=[{'changed': {'fields': ['Статус']}}],
    )