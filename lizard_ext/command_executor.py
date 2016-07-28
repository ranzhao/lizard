import subprocess


def execute(command):
    child = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    lines = child.communicate()[0]
    child.wait()
    return lines.split('\n')