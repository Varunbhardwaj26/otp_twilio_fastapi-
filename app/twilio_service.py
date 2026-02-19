from twilio.rest import Client


# SMS OTP 
def send_otp_sms(account_sid: str, auth_token: str, from_number: str, to_number: str, otp: str) -> str:
    """
    Twilio ko call karke SMS bhejta hai.
    Returns: message SID (Twilio message id)
    """

    client = Client(account_sid, auth_token)

    msg = client.messages.create(
        body=f"Your OTP is {otp}. It expires in 5 minutes.",
        from_=from_number,
        to=to_number
    )

    return msg.sid



# WHATSAPP OTP 

# WHATSAPP_SANDBOX_FROM = "whatsapp:+14155238886"

# def send_otp_whatsapp(account_sid: str, auth_token: str, to_number: str, otp: str) -> str:
#     """
#     Twilio WhatsApp Sandbox se OTP bhejta hai.
#     to_number must be like: +91XXXXXXXXXX
#     """

#     client = Client(account_sid, auth_token)

#     to = f"whatsapp:{to_number}"
#     from_ = WHATSAPP_SANDBOX_FROM

#     # DEBUG (temporary)
#     print("TWILIO FROM:", from_)
#     print("TWILIO TO:", to)

#     msg = client.messages.create(
#         body=f"Your OTP is {otp}. It expires in 5 minutes.",
#         from_=from_,
#         to=to,
#     )

#     return msg.sid



# purna code 
# def send_otp_sms(account_sid: str, auth_token: str, from_number: str, to_number: str, otp: str) -> str:
#     """
#     Twilio ko call karke SMS bhejta hai.
#     Returns: message SID (Twilio message id)
#     """
#     client = Client(account_sid, auth_token)
#
#     msg = client.messages.create(
#         body=f"Your OTP is {otp}. It expires in 5 minutes.",
#         from_=from_number,
#         to=to_number
#     )
#     return msg.sid
