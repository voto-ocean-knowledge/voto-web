from voto.services.mail_service import list_emails
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class AddEmailViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.email = self.request_dict.email.strip()

    def validate(self):
        if not self.email:
            self.error = "Please complete all fields"
        emails = list_emails()
        print(emails)
        if self.email in emails:
            self.error = f"email {self.email} already registered"
