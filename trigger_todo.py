import app.services.todo as TodoService
import time


def trigger_todo():
    """
    well we will need the meta data like user id, but thats later
    """
    while True:
        time.sleep(1)
        TodoService.get_all_todos_and_trigger()


if __name__ == "__main__":
    trigger_todo()
