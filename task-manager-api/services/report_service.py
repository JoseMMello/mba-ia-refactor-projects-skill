from datetime import timedelta

from models.category import Category
from models.task import (
    PRIORITY_LABELS, STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING,
    TASK_STATUSES, Task,
)
from models.user import User
from utils.helpers import calculate_percentage, utc_now

RECENT_ACTIVITY_DAYS = 7


def _overdue_tasks(now):
    overdue = []
    for task in Task.find_with_due_date():
        if task.is_overdue(now):
            overdue.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (now - task.due_date).days
            })
    return overdue


def _user_productivity():
    counts_by_user = Task.count_by_user_and_status()
    productivity = []
    for user in User.find_all():
        status_counts = counts_by_user.get(user.id, {})
        total = sum(status_counts.values())
        completed = status_counts.get(STATUS_DONE, 0)
        productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total)
        })
    return productivity


def build_summary_report():
    now = utc_now()
    recent_since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    status_counts = Task.count_by_status()
    priority_counts = Task.count_by_priority()
    overdue_tasks = _overdue_tasks(now)

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count_all(),
            'total_users': User.count_all(),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': {status: status_counts.get(status, 0) for status in TASK_STATUSES},
        'tasks_by_priority': {
            label: priority_counts.get(priority, 0) for priority, label in PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': overdue_tasks,
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(recent_since),
            'tasks_completed_last_7_days': Task.count_done_since(recent_since),
        },
        'user_productivity': _user_productivity(),
    }


def build_user_report(user):
    now = utc_now()
    tasks = Task.find_by_user(user.id)
    status_counts = {status: 0 for status in TASK_STATUSES}
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.is_high_priority():
            high_priority += 1
        if task.is_overdue(now):
            overdue += 1

    total = len(tasks)
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': status_counts[STATUS_DONE],
            'pending': status_counts[STATUS_PENDING],
            'in_progress': status_counts[STATUS_IN_PROGRESS],
            'cancelled': status_counts[STATUS_CANCELLED],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(status_counts[STATUS_DONE], total)
        }
    }
