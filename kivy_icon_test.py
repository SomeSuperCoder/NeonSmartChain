import subprocess
import platform


def ping(host):
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

# Usage
ip = 'notgoogle.com'  # Google's public DNS server
if ping(ip):
    print(f"{ip} is up!")
else:
    print(f"{ip} is down!")
