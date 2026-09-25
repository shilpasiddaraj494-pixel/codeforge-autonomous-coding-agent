import pytest
from task_manager import Task, create_task, mark_completed, filter_completed, sort_by_priority


def test_create_task_normal():
    task = create_task("Buy groceries", priority=2)
    assert task.title == "Buy groceries"
    assert task.completed is False
    assert task.priority == 2


def test_create_task_invalid_priority():
    with pytest.raises(ValueError):
        create_task("Bad priority", priority=0)
    with pytest.raises(ValueError):
        create_task("Bad priority", priority=6)
    with pytest.raises(ValueError):
        create_task("Bad priority", priority="high")


def test_mark_completed():
    tasks = [create_task("Task 1"), create_task("Task 2")]
    mark_completed(tasks, "Task 1")
    assert tasks[0].completed is True
    assert tasks[1].completed is False

    with pytest.raises(ValueError, match="not found"):
        mark_completed(tasks, "Nonexistent")


def test_mark_completed_duplicate_titles():
    tasks = [create_task("Repeat", priority=3), create_task("Repeat", priority=1)]
    mark_completed(tasks, "Repeat")
    assert tasks[0].completed is True
    assert tasks[1].completed is False


def test_filter_completed():
    t1 = create_task("A", completed=True)
    t2 = create_task("B", completed=False)
    t3 = create_task("C", completed=True)
    
    completed_tasks = filter_completed([t1, t2, t3])
    assert completed_tasks == [t1, t3]


def test_filter_completed_empty():
    assert filter_completed([]) == []


def test_sort_by_priority():
    t1 = create_task("Low", priority=3)
    t2 = create_task("High", priority=1)
    t3 = create_task("Medium", priority=2)

    sorted_tasks = sort_by_priority([t1, t2, t3])
    assert sorted_tasks == [t2, t3, t1]


def test_sort_by_priority_empty():
    assert sort_by_priority([]) == []
