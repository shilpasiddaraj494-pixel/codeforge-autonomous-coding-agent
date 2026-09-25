from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class Task:
    title: str
    completed: bool = False
    priority: int = 1


def create_task(title: str, priority: int = 1, completed: bool = False) -> Task:
    """Create a new Task with validation for priority."""
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ValueError("Priority must be an integer.")
    if not (1 <= priority <= 5):
        raise ValueError("Priority must be between 1 and 5.")
    return Task(title=title, completed=completed, priority=priority)


def mark_completed(tasks: List[Task], title: str) -> None:
    """Mark the first task with the given title as completed. Supports duplicate titles by marking the first match found."""
    for task in tasks:
        if task.title == title:
            task.completed = True
            return
    raise ValueError(f"Task with title '{title}' not found.")


def filter_completed(tasks: Sequence[Task]) -> List[Task]:
    """Return a list of tasks that are completed."""
    return [task for task in tasks if task.completed]


def sort_by_priority(tasks: Sequence[Task]) -> List[Task]:
    """Return a new list of tasks sorted by priority (ascending, where 1 is highest priority)."""
    return sorted(tasks, key=lambda t: t.priority)
