import docker
import re
import json

from docker.errors import ContainerError
from .report import report
from .schedule import catch_exceptions, with_logging

@catch_exceptions
@with_logging
def excute_with_docker(task):
    module, _ = create_module(task['code'])
    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name='nproc', soft=1024)
    cpu_limit = docker.types.Ulimit(name='cpu', soft=1024)
    try:
        log = client.containers.run(
            'python:latest',
            'python -c \"' + module+'\"',
            stdout=True, # record stdout
            stderr=True, # record stderr
            labels={"title": task['title']}, # label our docker container
            #mem_limit='100m',
            #ulimits=[nproc_limit, cpu_limit]
        )
        result = json.loads(log.decode("utf-8"))
        report(task, result)
    except ContainerError as e:
        raise e

def create_module(code):
    lines = ["import json", "result = dict()"]
    offset = len(lines) + 1
    outputLine = "\nprint(json.dumps(result))"
    return "\n".join(lines) + "\n" + code + outputLine, offset