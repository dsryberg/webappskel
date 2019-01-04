import json
from docker.errors import NotFound


def get_process_names(container):
    top = container.top()
    process_commands = [p[7] for p in top["Processes"]]
    gunicorn_processes = [p for p in process_commands if "gunicorn" in p]
    return gunicorn_processes


def get_config(container):
    gunicorn_processes = get_process_names(container)
    first_process = gunicorn_processes[0]
    first_part, partition, last_part = first_process.partition("-c")
    gunicorn_conf = last_part.strip().split()[0]
    result = container.exec_run(f"python {gunicorn_conf}")
    return json.loads(result.output.decode())


def stop_previous_container(client):
    try:
        previous = client.containers.get("uvicorn-gunicorn-test")
        previous.stop()
        previous.remove()
    except NotFound:
        return None