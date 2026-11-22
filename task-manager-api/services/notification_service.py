import logging
import smtplib

from config.settings import settings
from utils.helpers import utc_now

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, config=settings):
        self.notifications = []
        self.email_host = config.SMTP_HOST
        self.email_port = config.SMTP_PORT
        self.email_user = config.SMTP_USER
        self.email_password = config.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info('Email enviado')
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception('Erro ao enviar email')
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utc_now()
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications
                if notification['user_id'] == user_id]
