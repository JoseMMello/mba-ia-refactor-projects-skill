from sqlalchemy import func
from sqlalchemy.orm import joinedload

from database import db
from utils.helpers import utc_now

STATUS_PENDING = 'pending'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_DONE = 'done'
STATUS_CANCELLED = 'cancelled'
TASK_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_CANCELLED]
# A task in one of these statuses is finished and is never overdue.
CLOSED_STATUSES = [STATUS_DONE, STATUS_CANCELLED]

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
# Priorities from 1 up to this value count as high priority in the reports.
HIGH_PRIORITY_LIMIT = 2
PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}
TAG_SEPARATOR = ','


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(TAG_SEPARATOR) if self.tags else [],
        }

    def is_overdue(self, now=None):
        if not self.due_date:
            return False
        if self.status in CLOSED_STATUSES:
            return False
        return self.due_date < (now or utc_now())

    def is_high_priority(self):
        return self.priority is not None and self.priority <= HIGH_PRIORITY_LIMIT

    def touch(self):
        self.updated_at = utc_now()

    # Queries

    @classmethod
    def find_all_with_relations(cls):
        """All tasks with their user and category loaded in the same query."""
        return cls.query.options(joinedload(cls.user), joinedload(cls.category)).all()

    @classmethod
    def find_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            pattern = f'%{text}%'
            query = query.filter(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.all()

    @classmethod
    def count_all(cls):
        return cls.query.count()

    @classmethod
    def _count_grouped_by(cls, column):
        rows = db.session.query(column, func.count(cls.id)).group_by(column).all()
        return {key: count for key, count in rows}

    @classmethod
    def count_by_status(cls):
        return cls._count_grouped_by(cls.status)

    @classmethod
    def count_by_priority(cls):
        return cls._count_grouped_by(cls.priority)

    @classmethod
    def count_by_user(cls):
        return cls._count_grouped_by(cls.user_id)

    @classmethod
    def count_by_category(cls):
        return cls._count_grouped_by(cls.category_id)

    @classmethod
    def count_by_user_and_status(cls):
        """Returns {user_id: {status: count}} with a single grouped query."""
        rows = (db.session.query(cls.user_id, cls.status, func.count(cls.id))
                .group_by(cls.user_id, cls.status).all())
        counts = {}
        for user_id, status, count in rows:
            counts.setdefault(user_id, {})[status] = count
        return counts

    @classmethod
    def find_with_due_date(cls):
        return cls.query.filter(cls.due_date.isnot(None)).all()

    @classmethod
    def count_created_since(cls, moment):
        return cls.query.filter(cls.created_at >= moment).count()

    @classmethod
    def count_done_since(cls, moment):
        return cls.query.filter(cls.status == STATUS_DONE, cls.updated_at >= moment).count()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
