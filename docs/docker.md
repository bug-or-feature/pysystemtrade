How to run a complete *pysystemtrade* system as a suite of docker containers

#### run a complete system

* install docker
* copy the example environment file (/examples/docker/.env.example) to the top level
of the project, and rename it '.env'
* insert your IB credentials, and comment/uncomment appropriately depending
on whether you want to connect to IB in 'live' or 'paper' mode
* define a VNC password. The text can be anything you like
* on the commandline at the top level directory, run

``` docker-compose up -d```

* once the command finishes, you should have
  * a container running mongodb
  * a container running mongo-express, a web based UI for mongo
  * a container running IB gateway, with VNC enabled
  * a network connecting them all
  * a container with pysystemtrade and its dependencies installed, and
environment configured

* to execute commands on the pysystemtrade container

```docker exec -it pysystemtrade bash```

* to view the mongodb state via mongo-express, point a browser to

```http://localhost:8082```

* to view IB gateway, see output logs, point your VNC client to

```vnc://localhost:5901```

* rebuild and run pysystemtrade image after making changes

```docker-compose up -d --build```

* to stop containers, networks, images, volumes

```docker-compose down```

#### build and tag a pysystemtrade image

```docker image build -t pysystemtrade .```
