import requests
import subprocess
import platform
import os

SERVER_URL = "http://your-server-url"  # Replace with your server URL

def check_updates():
    distro = platform.linux_distribution()[0].lower()
    update_command = {
        'ubuntu': 'apt list --upgradable',
        'fedora': 'dnf check-update',
        'redhat': 'yum check-update'
    }.get(distro)

    if update_command is None:
        print(f"Unsupported distro: {distro}")
        return False

    result = subprocess.run(update_command.split(), capture_output=True, text=True)
    return len(result.stdout.strip()) > 0

def check_reboot_required():
    return os.path.exists('/var/run/reboot-required')

def report_to_server(name, update_status, reboot_required):
    response = requests.post(f"{SERVER_URL}/add-computer", json={
        'name': name,
        'update_status': update_status,
        'reboot_required': reboot_required
    })
    return response.status_code == 200

if __name__ == "__main__":
    name = platform.node()
    update_status = check_updates()
    reboot_required = check_reboot_required()
    success = report_to_server(name, update_status, reboot_required)

    if success:
        print("Reported to server successfully")
    else:
        print("Failed to report to server")