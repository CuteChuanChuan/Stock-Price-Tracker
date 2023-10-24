import datetime
import smtplib
from email.message import EmailMessage
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv(verbose=True)


def notify(data, operating_status: dict):
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    receivers = [os.getenv("RECEIVERS")]

    # ToDo: tidy text
    messages_html = pd.DataFrame(data).to_html(justify="center")

    # ToDo: Notify
    for receiver in receivers:
        msg = EmailMessage()
        if data.shape[0] == 0:
            msg[
                "Subject"
            ] = f"Stock Notification: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (無股票符合條件)"
        else:
            msg[
                "Subject"
            ] = f"Stock Notification: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg["From"] = user
        msg["To"] = receiver

        if data.shape[0] == 0:
            msg.set_content("此次無符合條件的股票，可忽略此信", subtype="plain")
        else:
            msg.set_content(messages_html, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com") as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)

    operating_status["send_emails"] = "success"
    return operating_status


if __name__ == "__main__":
    pass
