from copy import deepcopy

from app.agents.review_context import ReviewContext

_TASKS: dict[str, ReviewContext] = {}


def save_task(context: ReviewContext) -> ReviewContext:
    _TASKS[context["taskId"]] = deepcopy(context)
    return deepcopy(context)


def get_task(task_id: str) -> ReviewContext | None:
    task = _TASKS.get(task_id)
    return deepcopy(task) if task else None
