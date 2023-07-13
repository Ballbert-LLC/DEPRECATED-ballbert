**install git**

`sudo apt install git`

Do you want to continue? [Y/n]

`Y`

**Clone repo**

`git clone https://github.com/seesi8/hal.git`

`cd hal`

**install docker**

```
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg

    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/raspbian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/raspbian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Do you want to continue? [Y/n]

`Y`

```
    sudo apt-get update
    sudo apt-get install python3-pip
```

Do you want to continue? [Y/n]

`Y`

`sudo apt-get install build-essential libssl-dev libffi-dev python-dev`
