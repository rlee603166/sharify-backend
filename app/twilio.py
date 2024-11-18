import os
from twilio.rest import Client
from dependencies import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

client = Client(os.getenv["TWILIO_ACCOUNT_SID"], os.getenv["TWILIO_AUTH_TOKEN"])

verification = client.verify.v2.services(
    "VAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
).verifications.create(to="+15017122661", channel="sms")

print(verification.sid)