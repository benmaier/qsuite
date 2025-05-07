from __future__ import print_function
import paramiko
import select
import os
import sys
from dotenv import dotenv_values
from pathlib import Path

def ssh_command(ssh,command,noprint=False):
    """
    this is adapted from code by Sebastian Dahlgren
    http://sebastiandahlgren.se/2012/10/11/using-paramiko-to-send-ssh-commands/
    """

    # Send the command (non-blocking)
    print("ssh> " + command)
    stdin,stdout,stderr = ssh.exec_command(command)

    # Wait for the command to terminate
    last_line = ''
    complete_received = ''
    while not stdout.channel.exit_status_ready():
    # Only print data if there is data to read in the channel
        while stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
            if len(rl) > 0:
        # Print data from stdout
                recv = stdout.channel.recv(1024).decode('ascii')
                lines = recv.split('\n')
                if len(lines)>1:
                    first_lines = '\n'.join(lines[:-1]) + '\n'
                    received = last_line + first_lines
                    last_line = lines[-1]
                else:
                    last_line = ''
                    received = recv
                complete_received += received
                if not noprint:
                    sys.stdout.write(received)

    while stdout.channel.recv_ready():
        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
        if len(rl) > 0:
            # Print data from stdout
            recv = stdout.channel.recv(1024).decode('ascii')
            lines = recv.split('\n')
            if len(lines)>1:
                first_lines = '\n'.join(lines[:-1]) + '\n'
                received = last_line + first_lines
                last_line = lines[-1]
            else:
                last_line = ''
                received = recv
            complete_received += received
            if not noprint:
                sys.stdout.write(received)


    if (last_line is not None) and (last_line != "") and (not last_line.endswith("\n")):
        if not noprint:
            sys.stdout.write(last_line+"\n")
        complete_received += last_line+"\n"

    err = '\n'.join(stderr.read().decode('utf-8').split('\n')[:-1])
    if err != '' and not noprint:
        print(err)

    return complete_received


def ssh_connect(cf):
    """
    this is adapted from code by Sebastian Dahlgren
    http://sebastiandahlgren.se/2012/10/11/using-paramiko-to-send-ssh-commands/
    """
    try:
        key = get_ssh_key()
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cf.server,username=cf.username, pkey=key)
        print("Connected to %s" % cf.server)
    except paramiko.AuthenticationException as e:
        print("Authentication failed when connecting to %s" % cf.server)
        print("error:",e)
        sys.exit(1)
    except Exception as e:
        print("Couldn't establish an ssh connection to %s" % cf.server)
        print("error:", e)
        sys.exit(1)

    return ssh


def get_ssh_key():
    """loads the ssh-key:
            if .env exists: from entries in .env
                - use RSA or Ed25519 depending on name
            elif ~/.ssh/id_rsa_groot: use this one
    """
    f_env = Path.cwd() / '.env'

    # ======== determine key-file ========
    f_default_key = Path('~/.ssh/id_rsa_groot').expanduser()
    with_pw = False
    if f_env.exists():
        env_variables = dotenv_values('.env')
        if Path(env_variables['pkey_file']).exists():
            f_key = Path(env_variables['pkey_file'])
        if 'password' in env_variables.keys():
            with_pw = True
    elif f_default_key.exists():
        f_key = f_default_key
    else:
        raise FileNotFoundError("No valid key found in .env or ~/.ssh/id_rsa_groot")

    # ======== determine key-method ========
    if 'ed25519' in f_key.parts[-1].lower():
        key_method = paramiko.Ed25519Key
    elif 'rsa' in f_key.parts[-1].lower():
        key_method = paramiko.RSAKey
    else:
        raise ValueError("No valid key [ed25519, rsa] found in .env --> either rename key or add new key-detection-method")

    # ======== load key with or without pw ========
    if with_pw:
        key = key_method.from_private_key_file(f_key, password=env_variables['password'])
    else:
        key = key_method.from_private_key_file(f_key)
    return key

def print_progress(transferred, toBeTransferred):
    progress = transferred / float(toBeTransferred)
    _update_progress(progress)

def _update_progress(progress, bar_length=40, status=""):
    """
    This function was coded by Marc Wiedermann (https://github.com/marcwie)

    Draw a progressbar according to the actual progress of a calculation.

    Call this function again to update the progressbar.

    :type progress: number (float)
    :arg  progress: Percentile of progress of a current calculation.

    :type bar_length: number (int)
    :arg  bar_length: The length of the bar in the commandline.

    :type status: str
    :arg  status: A message to print behing the progressbar.
    """
    block = int(round(bar_length*progress))
    text = "\r[{0}] {1:4.1f}% {2}".format("="*block + " "*(bar_length-block),
                                     round(progress, 3)*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    #if progress >= 1:
    #    sys.stdout.write("\n")

def sftp_put_files(ssh,cf,files_destinations):

    #ssh_command(ssh,
    #            "mkdir -p "+cf.serverpath+"; "+\
    #            "mkdir -p "+cf.resultpath+"; "+\
    #            "mkdir -p "+cf.serverpath+"/output")

    #additional_directories = set([cf.serverpath, cf.resultpath, cf.serverpath+"/output"])
    all_directories = set()
    mkdir_p_string = "mkdir -p "+cf.serverpath+"/output; mkdir -p "+cf.resultpath+"; "

    for f,d in files_destinations:
        directory = '/'.join(d.split('/')[:-1])

        if directory not in all_directories:
            all_directories.add(directory)
            mkdir_p_string += 'mkdir -p ' + directory + "; "

    ssh_command(ssh,mkdir_p_string)
    ftp = ssh.open_sftp()

    for f,d in files_destinations:
        print(" "+f+"\n =>"+d)
        ftp.put(f,d,callback=print_progress)
        sys.stdout.write("\n")

def sftp_get_files(ssh,cf,files_destinations):

    ftp = ssh.open_sftp()

    for f,d in files_destinations:
        print(" "+f+"\n =>"+d)
        ftp.get(f,d,callback=print_progress)
        sys.stdout.write("\n")
