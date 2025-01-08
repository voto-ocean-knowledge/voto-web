import datetime
from voto.data.db_classes import Glider
from voto.services.schedule_service import user_is_piloting, read_schedule, time_pretty
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
from voto.services import user_service
import random
import os
import json

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


class AccountViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.user = user_service.find_user_by_id(self.user_id)
        self.piloting = user_is_piloting(self.user_id)
        self.name = self.user.name.lower()
        self.alarm_me = self.request_dict.alarm_me
        if self.piloting:
            self.alarm_me = True
        if self.piloting:
            self.user_message = "⚡ Stay vigilant Pilot ⚡"
        else:
            self.user_message = "Relax, you're off duty 😴"
        schedule = read_schedule()
        self.schedule = schedule[
            schedule.index
            > datetime.datetime.combine(
                datetime.date.today(), datetime.datetime.min.time()
            )
        ]
        df = schedule[
            schedule.index > datetime.datetime.now() - datetime.timedelta(hours=1)
        ]
        if self.name in df.pilot.values and not self.piloting:
            next_on = df[df.pilot == "callum"].index.min()
            in_time = time_pretty(next_on - datetime.datetime.now())
            self.next_shift = f"Your next shift starts at {next_on} UTC (in {in_time})."
        gliders = Glider.objects().order_by("glider")
        for glider in gliders:
            glider.glider_fill = str(glider.glider).zfill(3)
        glider_grid = []
        glider_list = []
        for i, glider in enumerate(gliders):
            glider_list.append(glider.glider)
            if (i + 1) % 3 == 0:
                glider_grid.append(glider_list)
                glider_list = []
        self.glider_grid = glider_grid

        self.gliders = gliders
        sink_links = [
            "https://images.fineartamerica.com/images/artworkimages/mediumlarge/1/chance-card-vintage-monopoly-go-directly-to-jail-design-turnpike.jpg",
            "https://i.giphy.com/wVG5iaHYWS3eT1I2EY.webp",
            "https://c.tenor.com/FRYZ7FnxC8UAAAAC/tenor.gif",
            "https://sv.wikipedia.org/wiki/Regalskeppet_Vasa#Jungfruf%C3%A4rden",
            "https://media.timeout.com/images/100654045/image.jpg",
            "https://callumrollo.com/files/frederik_short.mp3",
        ]
        if datetime.datetime.now() - self.user.date_added < datetime.timedelta(hours=1):
            sink_links = sink_links[:3]
        self.sink_link = random.choice(sink_links)
        if random.randint(0, 99) == 7:
            self.sink_link = "https://youtu.be/dQw4w9WgXcQ?si=njkBEY1tTO75UUrR&t=43"


class RegisterViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.name = self.request_dict.name
        self.email = self.request_dict.email.lower().strip()
        self.secret = self.request_dict.secret.lower().strip()
        self.password = self.request_dict.password.strip()

    def validate(self):
        if not self.name or not self.name.strip():
            self.error = "You must specify a name."
        elif not self.email or not self.email.strip():
            self.error = "You must specify an email."
        elif self.secret != secrets["magic_word"]:
            self.error = "You didn't say the magic word"
        elif not self.password:
            self.error = "You must specify a password."
        elif len(self.password.strip()) < 8:
            self.error = "The password must be at least 8 characters."
        elif user_service.find_user_by_email(self.email):
            self.error = "A user with that email address already exists."


class LoginViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.email = self.request_dict.email.lower().strip()
        self.password = self.request_dict.password.strip()

    def validate(self):
        if not self.email or not self.email.strip():
            self.error = "You must specify a email."
        elif not self.password:
            self.error = "You must specify a password."
