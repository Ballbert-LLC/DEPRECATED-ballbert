import os


os.system("sudo rm -f- r /opt/ballbert")
os.system("sudo git clone --depth 1 https://github.com/Ballbert-LLC/ballbert.git ")
os.system("sudo cd /opt/ballbert")
os.system("sudo python3 update.py")
autostart_file = "/etc/xdg/lxsession/LXDE-pi/autostart"
os.system(
    f'echo "@sudo /opt/ballbert/start.sh" | sudo tee "{autostart_file}" > /dev/null'
)
