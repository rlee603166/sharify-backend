import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)


verification = client.verify.v2.services(
    "VA36043d17f0c4c1630d225be4056ae495"
).verifications.create(to="+13108745772", channel="sms")


# verification_check = client.verify.v2.services(
#     "VA36043d17f0c4c1630d225be4056ae495"
# ).verification_checks.create(to="+13108745772", code="834697")

print(verification_check.status)