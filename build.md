**install git**

`sudo apt install git`

Do you want to continue? [Y/n]

`Y`

**Clone repo**

`git clone https://github.com/seesi8/hal.git`

`cd hal`

**install docker**

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

`sudo apt-get install build-essential libssl-dev libffi-dev python-dev`

```
    python-dotenv
    fastapi
    uvicorn
    sqlite3
    pvporcupine
    openai
    pvrecorder
    PyYAML
    docstring-parser
    weaviate
    tiktoken
    git
    simpleaudio
    google-cloud-texttospeech
    pydub
```
