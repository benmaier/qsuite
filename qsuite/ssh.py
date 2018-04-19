from __future__ import print_function
import paramiko
import select
import os
import sys

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
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cf.server,username=cf.username)
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
