# -*- coding: utf-8 -*-
import requests
import json
import sys
import datetime
from twilio.rest import Client
import datetime
from django.conf import settings
from please_marketing_app.models import SmsHistory


# from please_marketing_growth_hack.merchant_sign_up.sign_up import *
def send_sms_fail_password_or_email(first_name, phone):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(", malheureusement la création de votre compte Please n'a pas pu être finalisée car votre adresse "
                      "email est déjà utilisée par un autre compte. Merci de réessayer avec une nouvelle adresse.")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: send_sms_fail_password_or_email sent to user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - In-Store Sign Up (failed pwd or email)"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def send_sms_fail_password(first_name, phone):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(", malheureusement la création de votre compte Please n'a pas pu être finalisée car votre "
                      "mot de passe ne respecte pas notre politique de sécurité. Merci de réessayer avec un "
                      "mot de passe comprenant 8 caractères, 1 majuscule et 1 chiffre minimum.")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: send_sms_fail_password sent to user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - In-Store Sign Up (failed pwd)"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def sign_up_please(
        email,
        first_name,
        last_name,
        pwd,
        phone,
        street,
        city,
        zip,
        longitude,
        latitude,
        odoo_conciergerie_id,
        cgu_id,
        marketing):

    now = datetime.datetime.now()
    cgu_date = str(now.strftime("%Y-%m-%dT%H:%M:%S"))

    try:

        url = "https://mw.please-it.com/next-mw/api/public/user"

        payload = {
            "developerMode": False,
            "marketingSubscription": marketing,
            "subscribed": False,
            "email": str(email),
            "pwd": str(pwd),
            "billingAddress": {
                "street": str(street),  # "12 Rue de la Mairie",
                "city": str(city),  # "Mantes-la-Ville",
                "zip": str(zip),  # "78711",
                "type": "housenumber",
                "label": str(str(street) + " " + str(zip) + " " + str(city)),  # "12 Rue de la Mairie 78711 Mantes-la-Ville",
                "coordinate": {
                    "longitude": longitude,  # 1.712679,
                    "latitude": latitude,  # 48.978537
                },
                "building": "",
                "digicode": "",
                "floor": "",
                "elevator": "",
                "door": "",
                "details": ""
            },
            "linkedToConciergerie": True,
            "odooConciergerieId": int(odoo_conciergerie_id),  # 4,
            "firstName": str(first_name),
            "lastName": str(last_name),
            "mobileNumber": str(phone),  # "0677543333",
            "cguDate": cgu_date,  # "2019-01-10T01:32:14",
            "cguId": int(cgu_id),  # 102,
            "cguValid": True
        }

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'X-Accept-Version': "1.9",
            }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers).json()
        print(response)

        if response.get("statusCode") == 500:
            print("ERROR: Not able to create a user through on-site sign-up process - ERREUR 500 from Please")
            send_sms_fail_password_or_email(first_name=first_name, phone=phone)

        if response.get("statusCode") == 400:
            print("ERROR: Not able to create a user through on-site sign-up process - ERREUR 400 from Please")
            send_sms_fail_password(first_name=first_name, phone=phone)

        else:
            odoo_user_id = response.get("odooId")
            return odoo_user_id

    except:
        print("ERROR: Not able to create a user through on-site sign-up process - " + str(sys.exc_info()))
        send_sms_fail_password_or_email(first_name=first_name, phone=phone)

    return
