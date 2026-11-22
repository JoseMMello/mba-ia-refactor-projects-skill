from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.helpers import utc_now

USER_ROLES = ['user', 'admin', 'manager']
DEFAULT_ROLE = 'user'
MIN_PASSWORD_LENGTH = 4


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        try:
            return check_password_hash(self.password, raw_password)
        except ValueError:
            # Hash stored in a format werkzeug does not know (rows written before the refactor).
            return False

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def count_all(cls):
        return cls.query.count()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete_with_tasks(self):
        """Deletes the user and the tasks assigned to them in one transaction."""
        try:
            for task in list(self.tasks):
                db.session.delete(task)
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
