from voto.services.user_service import find_user_by_id
import pandas as pd
import datetime
from pathlib import Path
import json
import numpy as np

script_dir = Path(__file__).parent.parent.parent.absolute()
with open("contacts_secrets.json", "r") as secrets_file:
    contacts = json.load(secrets_file)


def user_is_piloting(user_id):
    if not user_id:
        return False
    user = find_user_by_id(user_id)
    if not user:
        return False
    pilot, supervisor = current_pilot()
    if pilot.lower() in user.name.lower():
        return True
    else:
        return False


def read_schedule(phone_numbers=False):
    schedule = pd.read_csv(
        "/data/log/schedule.csv", parse_dates=True, index_col=0, sep=";", dtype=str
    )
    schedule = schedule.replace(np.nan, "")
    if phone_numbers:
        for name, number in contacts.items():
            schedule.replace(name, number, inplace=True, regex=True)
    return schedule


def current_pilot():
    schedule = read_schedule()
    now = datetime.datetime.now()
    row = schedule[schedule.index < now].iloc[-1]
    pilot_phone = row["pilot"]
    supervisor_phone = row["supervisor"]
    if type(supervisor_phone) is float:
        supervisor_phone = None
    return pilot_phone, supervisor_phone


def time_pretty(dt):
    seconds = int(dt.seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return f"{days} days {hours} hours {minutes} minutes"
    elif hours > 0:
        return f"{hours} hours {minutes} minutes"
    else:
        return f"{minutes} minutes"
