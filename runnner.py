import json
import subprocess
import sys
import re

def execute(code, context):
    module, offset = create_module(code.code, context)
    # executable binary for the Python interpreter
    with subprocess.Popen([sys.executable, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        communicate(process, code, module, offset)

def create_module(code, context):
    lines = ["import json", "result = dict()"]
    for k,v in context.items():
        lines.append("{} = {!r}".format(k,v))
    offset = len(lines) + 1
    outputLine = "\nprint(json.dumps(result))"
    return "\n".join(lines) + "\n" + code + outputLine, offset

def communicate(process, code, module, offset):
    stdout, stderr = process.communicate(module.encode('utf-8'))
    if stderr:
        stderr = stderr.decode('utf-8').lstrip().replace(", in <module>", ":")
        stderr = re.sub(", line(\d+)", lambda match: str(int(match.group(1)) - offset), stderr)
        print(re.sub(r'File."[^"]+?"', "'{}' has an error on line ".format(code.name), stderr))
        return
    if stdout:
        result, error = json.loads(stdout.decode("utf-8"))
        handle_result(code, result, error)
        return
    print("'{}' produced no result\n".format(code.name))

def handle_result():
    