from voto.data.db_classes import User
from voto.services.user_service import find_user_by_id
import pandas as pd
import datetime
from pathlib import Path
import json
import numpy as np

script_dir = Path(__file__).parent.parent.parent.absolute()
with open(script_dir / "contacts_secrets.json", "r") as secrets_file:
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
    pilot = row["pilot"]
    supervisor = row["supervisor"]
    if type(supervisor) is float:
        supervisor = None
    return pilot, supervisor


def time_pretty(dt):
    seconds = int(dt.seconds)
    days = dt.days
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return f"{days} days {hours} hours {minutes} minutes"
    elif hours > 0:
        return f"{hours} hours {minutes} minutes"
    else:
        return f"{minutes} minutes"


def currently_alarmed_users():
    pilot, __ = current_pilot()
    alarm_users = User.objects(alarm=True)
    alarm_usernames = {user.to_mongo().to_dict()["name"] for user in alarm_users}.union(
        [pilot]
    )
    surface_users = User.objects(alarm_surface=True)
    surface_usernames = {user.to_mongo().to_dict()["name"] for user in surface_users}
    return alarm_usernames, surface_usernames


def users_table():
    users = User.objects().as_pymongo()
    pilot, __ = current_pilot()
    df = pd.DataFrame(list(users))
    df.loc[df.name == pilot, "alarm"] = True
    df.index = df.user_id
    df = df.drop(["hashed_password", "_id", "user_id"], axis=1)
    df["date_added"] = df["date_added"].astype(str).str[:10]
    df["last_login"] = df["last_login"].astype(str).str[:16]
    return df
