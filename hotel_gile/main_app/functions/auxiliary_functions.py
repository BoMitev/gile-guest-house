from datetime import datetime, timedelta


def get_session_language(session):
    import hotel_gile.main_app.language_config as lang_config

    if 'language' not in session:
        session['language'] = lang_config.DEFAULT_LANGUAGE
        session.save()
    return session.get('language')


def default_check_in():
    today = datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime(year, month, day, 14, 00)


def default_check_out():
    today = datetime.today()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))

    return datetime(year, month, day, 12, 00) + timedelta(days=1)


def load_reviews():
    from hotel_gile.settings import REVIEW_API_URL, REVIEW_QUERYSTRING, REVIEW_HEADERS
    import requests
    import json

    response = requests.request("GET", REVIEW_API_URL, headers=REVIEW_HEADERS, params=REVIEW_QUERYSTRING)
    response_data = json.loads(response.text)
    reviews = response_data.get('result')

    return reviews, response.status_code


def get_content_type_for_model(obj):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


