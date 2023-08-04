import os

with open("/opt/ballbert_backups/updating_to.txt", "r") as file:
    version = file.read()

os.system("sudo rm -f- r /opt/ballbert")
os.system("sudo cd /opt")

os.system(
    f"sudo git clone --depth 1 -b {version} https://github.com/Ballbert-LLC/ballbert.git"
)
os.system("sudo cd /opt/ballbert")
os.system("sudo python3 update.py")
autostart_file = "/etc/xdg/lxsession/LXDE-pi/autostart"
os.system(
    f'echo "@sudo /opt/ballbert/start.sh" | sudo tee "{autostart_file}" > /dev/null'
)
os.system("sudo reboot")
