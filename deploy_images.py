#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""
Wrapper for Docker related utils.
"""


import docker
import os
import subprocess
import sys
import time


NO_OF_CONTAINERS = 2


def main():
    """Main thread."""

    cwd = sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    cmds_to_execute = ["docker-compose down -v ", "docker-compose up --detach --force-recreate --build"]
    for cmd in cmds_to_execute:
        sp = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            shell=True,
            cwd=cwd
        )
        # Poll process.stdout to show stdout live
        while True:
            output = sp.stdout.readline()
            if sp.poll() is not None:
                break

            if output:
                print(output.strip())

        return_code = sp.poll()
        if return_code != 0:
            print("Could not execute command: '{cmd}'".format(cmd=cmd))
            sys.exit(1)

    client = docker.from_env()

    # Wait for any restarting containers for 10 seconds
    count_down = 10
    while count_down > 0:
        list_of_restarting_containers = client.containers.list(filters={"status": "restarting"})
        if not list_of_restarting_containers:
            break

        print("Container(s) are restarting: {0}".format(list_of_restarting_containers))

        count_down -= 1
        time.sleep(1)

    list_of_containers = client.containers.list(filters={"status": "running"})
    if len(list_of_containers) < NO_OF_CONTAINERS:
        print("Not all containers are running!")
        sys.exit(1)


####################################################################################################
# Standard boilerplate to call the main() function to begin the program.
# This only runs if the module was *not* imported.
#
if __name__ == '__main__':
    main()
