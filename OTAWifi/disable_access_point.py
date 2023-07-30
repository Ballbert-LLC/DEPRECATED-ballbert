import os


def disable_access_point():
    os.system("systemctl disable dnsmasq")
    os.system("systemctl disableg hostapd")

    os.system("sudo cp /etc/dnsmasq.conf.copy /etc/dnsmasq.conf")
    os.system("sudo cp /etc/dhcpcd.conf.copy /etc/dhcpcd.conf")

    # Disable the Starup script

    os.system("reboot")
