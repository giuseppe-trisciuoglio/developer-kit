#!/usr/bin/env python3
import subprocess, sys

def get_current_branch():
    try:
        output = subprocess.check_output(['git', 'branch', '--show-current'], stderr=subprocess.STDOUT)
        branch = output.decode().strip()
        if not branch:
            return "detached HEAD"
        return branch
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error retrieving branch: " + e.output.decode() + "\n")
        sys.exit(1)

if __name__ == "__main__":
    print(get_current_branch())
