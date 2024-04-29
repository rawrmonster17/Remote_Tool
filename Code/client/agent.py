import os
import distro
import platform
import requests
import subprocess
import uuid


SERVER_URL = "http://192.168.1.201:8000"  # Replace with your server URL
uuid_based_on_host_id = uuid.uuid1()


def check_updates():
    try:
        distro_name = distro.id()
        update_command = {
            'ubuntu': 'apt list --upgradable',
            'debian': 'apt list --upgradable',  # Add this line
            'fedora': 'dnf check-update',
            'redhat': 'yum check-update'
        }.get(distro_name)

        if update_command is None:
            print(f"Unsupported distro: {distro_name}")
            return False

        result = subprocess.run(update_command.split(),
                                capture_output=True,
                                text=True)
        return len(result.stdout.strip()) > 0
    except Exception as e:
        print(f"An error occurred while checking updates: {e}")
        return False


def check_reboot_required():
    try:
        return os.path.exists('/var/run/reboot-required')
    except Exception as e:
        print(f"An error occurred while checking reboot status: {e}")
        return False


def report_to_server(comp_uuid, name, update_status, reboot_required):
    try:
        # Convert data types if needed
        comp_uuid = str(comp_uuid)
        name = str(name)
        update_status = bool(update_status)
        reboot_required = bool(reboot_required)

        # Prepare the payload as JSON
        payload = {
            "comp_uuid": comp_uuid,
            "name": name,
            "update_status": update_status,
            "reboot_required": reboot_required
        }

        # Send POST request with JSON payload
        response = requests.post(f"{SERVER_URL}/add-computer", json=payload)

        # Check response status code
        if response.status_code != 200:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"An error occurred while reporting to server: {e}")
        return False


if __name__ == "__main__":
    try:
        name = platform.node()
        update_status = check_updates()
        reboot_required = check_reboot_required()
        success = report_to_server(uuid_based_on_host_id,
                                   name,
                                   update_status,
                                   reboot_required)
        print(success)

        if success:
            print("Reported to server successfully")
        else:
            print("Failed to report to server")
    except Exception as e:
        print(f"An error occurred: {e}")
