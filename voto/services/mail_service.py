import logging
from voto.data.db_classes import EmailList

_log = logging.getLogger(__name__)


def add_email(email_address):
    mail = EmailList()
    # check if email already exists
    try:
        old_email = EmailList.objects(email=email_address).first()
    except:
        old_email = None
    if old_email:
        _log.info(f"email {email_address} already registered. Skipping")
        return None
    mail.email = email_address
    mail.save()
    _log.info(f"Add {email_address}")
    return mail


def list_emails():
    emails = EmailList.objects().only("email").as_pymongo()
    if not emails:
        return []
    mails = [e["email"] for e in emails]
    return mails
