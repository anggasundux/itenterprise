import requests
from django.conf import settings

def kirim_wa(pesan):

    url = "https://api.fonnte.com/send"

    headers = {
        "Authorization": settings.WA_TOKEN
    }

    for nomor in settings.WA_TARGETS:
        data = {
            "target": nomor,
            "message": pesan
        }

        requests.post(url, headers=headers, data=data)
