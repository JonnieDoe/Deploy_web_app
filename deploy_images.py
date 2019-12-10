#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""
Wrapper for Docker related utils.
"""


import docker
import getpass
import os
import smtplib
import ssl
import subprocess
import sys
import time


NO_OF_CONTAINERS = 2
GIT_URI = 'https://github.com/JonnieDoe/Deploy_web_app.git'
REPO_NAME = 'Deploy_web_app'
# Mail settings
SMTP_SERVER = "smtp.gmail.com"
PORT = 587  # For starttls


def send_mail():
    """Send mail to signal the containers are up and running."""
    sender_email = input("Sender mail address:  ")
    password = getpass.getpass("Type your password and press enter:  ")
    receiver_email = input("Receiver mail address:  ")
    message = """\
    Subject: Docker status

    Docker containers are up and running.."""

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def main():
    """Main thread."""

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cwd = sys.path.append(parent_dir)

    # Fetch the remote repo
    cmd = 'git clone {git_uri}'.format(git_uri=GIT_URI)
    sp = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
        shell=True,
        cwd=cwd
    )
    sp.wait()

    if sp.returncode != 0:
        print("Could not execute command: '{cmd}'".format(cmd=cmd))
        sys.exit(1)

    # Bring up the containers
    cmds_to_execute = ["docker-compose down -v", "docker-compose up --detach --force-recreate --build"]
    for cmd in cmds_to_execute:
        sp = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            shell=True,
            cwd=os.path.join(parent_dir, REPO_NAME)
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
        print("Not all containers are running! Exiting")
        sys.exit(1)

    print("\nAll containers are up and running: {list_of_containers}\n".format(list_of_containers=list_of_containers))

    try:
        send_mail()
    except Exception as exec_err:
        print("Could not send mail notification!\nReason: {reason}".format(reason=exec_err))


####################################################################################################
# Standard boilerplate to call the main() function to begin the program.
# This only runs if the module was *not* imported.
#
if __name__ == '__main__':
    main()
