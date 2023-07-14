**install git**

`sudo apt install git`

Do you want to continue? [Y/n]

`Y`

**Clone repo**

`git clone https://github.com/seesi8/hal.git`

`cd hal`

**Install Docker**

```
    # Install some required packages first
    sudo apt update
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg2 \
        software-properties-common

    # Get the Docker signing key for packages
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -

    # Add the Docker official repos
    echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
        $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list

    # Install Docker
    sudo apt update
    sudo apt install -y --no-install-recommends \
        docker-ce \
        cgroupfs-mount
```

```
    sudo apt-get update
    sudo apt-get install python3-pip
```

Do you want to continue? [Y/n]

`Y`

**Install Audio Dependancies**

`sudo apt-get install build-essential libssl-dev libffi-dev python-dev`

`sudo apt install python3-pyaudio`

`sudo apt-get install -y python3-dev libasound2-dev`

`pip install --upgrade pip setuptools`

`pip install simpleaudio`

`pip install PyAudio`

**Install Regular Dependancies**

`pip install -r requirements.txt`
