import paramiko
import select
import os
import sys

def ssh_command(ssh,command):
    """
    this is adapted from code by Sebastian Dahlgren
    http://sebastiandahlgren.se/2012/10/11/using-paramiko-to-send-ssh-commands/
    """

    # Send the command (non-blocking)
    print("ssh> " + command)
    stdin,stdout,stderr = ssh.exec_command(command)

    # Wait for the command to terminate
    received = None
    while not stdout.channel.exit_status_ready():
	# Only print data if there is data to read in the channel
	if stdout.channel.recv_ready():
	    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
	    if len(rl) > 0:
		# Print data from stdout
                received = stdout.channel.recv(1024)
		sys.stdout.write(received)
                
    if (received is not None) and (not received.endswith("\n")):
        sys.stdout.write("\n")

    err = '\n'.join(stderr.read().split('\n')[:-1])
    if err != "":
        print(err)


def ssh_connect(cf):
    """
    this is adapted from code by Sebastian Dahlgren
    http://sebastiandahlgren.se/2012/10/11/using-paramiko-to-send-ssh-commands/
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cf.server,username=cf.username)
        print("Connected to %s" % cf.server)
    except paramiko.AuthenticationException as e:
        print("Authentication failed when connecting to %s" % cf.server)
        print("error:",e)
        sys.exit(1)
    except:
        print("Couldn't establish an ssh connection to %s" % cf.server)

    return ssh

def sftp_put_files(ssh,cf,files_destinations):

    ssh_command(ssh,
                "mkdir -p "+cf.serverpath+"; "+\
                "mkdir -p "+cf.resultpath+"; "+\
                "mkdir -p "+cf.serverpath+"/output")

    ftp = ssh.open_sftp()

    for f,d in files_destinations:
        print(" "+f+"\n =>"+d)
        ftp.put(f,d)
