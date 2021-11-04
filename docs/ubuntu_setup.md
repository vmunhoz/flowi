# Ubuntu Setup

## Configure VNC

```
sudo apt update -y
sudo apt install ubuntu-desktop -y
sudo apt install tightvncserver -y
sudo apt install gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal -y

```
In your terminal type the following command to launch VNC server to create an initial configuration file:
```
 vncserver :1
```
Open the configuration file in vim:

```
nano ~/.vnc/xstartup
```
Change it to
```
#!/bin/sh

export XKL_XMODMAP_DISABLE=1
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
xsetroot -solid grey

vncconfig -iconic &
gnome-panel &
gnome-settings-daemon &
metacity &
nautilus &
gnome-terminal &
```

To kill the vnc server and start it again, type the following command:

```
vncserver -kill :1

vncserver :1
```
Launch Remmina Remote Desktop Client. Then, 1. Choose the connection type as ‘VNC’

Enter your EC2 url along with the port number as 1. For eg. : My EC2 instance URL and the port number as 1 will be

```
 ec2-54-172-197-171.compute-1.amazonaws.com:1
```
>!! Don't forget the **:1** at the end !!

Enter the password you provided during the installation of the VNC Server. Connect!

## Docker

Uninstall previous docker
```
sudo apt-get remove docker docker-engine docker.io containerd runc
```

Update the `apt` package index and install packages to allow `apt` to use a repository over HTTPS:
```
sudo apt-get update -y

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
```
Add Docker’s official GPG key:
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```
Use the following command to set up the **stable** repository.
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
Install Docker Engine
```
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
```

Manage Docker as a non-root user
```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker ps
```

### Configure Docker

Pushing images to this insecure registry may fail in some versions of Docker unless the daemon is explicitly configured to trust this registry. To address this we need to edit  `/etc/docker/daemon.json`  and add:

```
{
  "insecure-registries" : [
      "localhost:32000",
      "172.0.0.1:5000"
  ]
}
```

Change 172.0.0.1 by your container-registry ip.
```
kubectl get svc -n container-registry
```

#### Restart docker service
```
sudo service docker reload
sudo service docker restart
```
