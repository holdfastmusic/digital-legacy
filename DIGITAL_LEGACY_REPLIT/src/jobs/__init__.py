"""
Inactivity check job for succession plans.
Run periodically via cron or scheduler:
  python -m src.jobs.inactivity_check
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.main import app
from src.models.user import db, User
from src.models.succession_plan import SuccessionPlan
from src.models.beneficiary import Beneficiary
from src.models.asset_assignment import AssetAssignment
from src.models.digital_asset import DigitalAsset


SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER)


def send_warning_email(user, plan, days_since):
    days_left = plan.trigger_days - days_since
    subject = f"Digital Legacy — conferma la tua presenza ({days_left} giorni rimanenti)"
    body = (
        f"Ciao {user.name or user.username},\n\n"
        f"Non accedi a Digital Legacy da {days_since} giorni.\n"
        f"Il tuo piano di successione si attiverà tra {days_left} giorni.\n\n"
        f"Se stai bene, accedi all'app per resettare il timer:\n"
        f"POST /api/succession-plan/activity\n\n"
        f"— Digital Legacy"
    )
    _send_email(user.email, subject, body)


def send_trigger_email(user, beneficiary, assignments):
    subject = f"Digital Legacy — notifica di successione da {user.name or user.username}"
    asset_list = "\n".join(
        f"  - {a.asset.name} ({a.asset.asset_type}): {a.instructions or 'nessuna istruzione specifica'}"
        for a in assignments
    )
    body = (
        f"Ciao {beneficiary.name},\n\n"
        f"{user.name or user.username} ti ha designato come beneficiario "
        f"dei seguenti asset digitali:\n\n"
        f"{asset_list}\n\n"
        f"Per accedere alle credenziali, contatta il gestore del servizio.\n\n"
        f"— Digital Legacy"
    )
    _send_email(beneficiary.email, subject, body)


def _send_email(to, subject, body):
    if not SMTP_USER or not SMTP_PASS:
        print(f"[DRY RUN] Email to {to}: {subject}")
        return

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, to, msg.as_string())
    print(f"Email sent to {to}: {subject}")


def check_inactivity():
    with app.app_context():
        plans = SuccessionPlan.query.filter_by(status='active').all()
        print(f"Checking {len(plans)} active plans...")

        for plan in plans:
            user = User.query.get(plan.user_id)
            if not user:
                continue

            last = plan.last_activity or plan.created_at
            days_since = (datetime.utcnow() - last).days

            warning_threshold = int(plan.trigger_days * 0.66)

            if days_since >= plan.trigger_days:
                plan.status = 'triggered'
                db.session.commit()
                print(f"TRIGGERED: user {user.username} ({days_since} days)")

                beneficiaries = Beneficiary.query.filter_by(user_id=user.id).all()
                for ben in beneficiaries:
                    assignments = (
                        db.session.query(AssetAssignment)
                        .join(DigitalAsset)
                        .filter(AssetAssignment.beneficiary_id == ben.id)
                        .filter(DigitalAsset.user_id == user.id)
                        .all()
                    )
                    if assignments:
                        send_trigger_email(user, ben, assignments)

            elif days_since >= warning_threshold:
                print(f"WARNING: user {user.username} ({days_since}/{plan.trigger_days} days)")
                send_warning_email(user, plan, days_since)


if __name__ == '__main__':
    check_inactivity()
