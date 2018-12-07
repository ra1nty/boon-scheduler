import re
import json
import subprocess

from .report import report
from .schedule import catch_exceptions, with_logging

@catch_exceptions
@with_logging
def execute(task):
    module, offset = create_module(task['code'])
    # executable binary for the Python interpreter
    with subprocess.Popen([sys.executable, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        communicate(process, task, module, offset)

def create_module(code):
    lines = ["import json", "result = dict()"]
    offset = len(lines) + 1
    outputLine = "\nprint(json.dumps(result))"
    return "\n".join(lines) + "\n" + code + outputLine, offset

def communicate(process, task, module, offset):
    stdout, stderr = process.communicate(module.encode('utf-8'))
    if stderr:
        stderr = stderr.decode('utf-8').lstrip().replace(", in <module>", ":")
        stderr = re.sub(r", line(\d+)", lambda match: str(int(match.group(1)) - offset), stderr)
        print(re.sub(r'File."[^"]+?"', "'{}' has an error on line ".format(task['title']), stderr))
        return
    if stdout:
        result = json.loads(stdout.decode("utf-8"))
        report(task, result)
        return
    print("'{}' produced no result\n".format(task['title']))
