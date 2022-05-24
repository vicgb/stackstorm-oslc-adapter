# Stackstorm OSLC Adapter

Trabajo Fin de Master: Design and implementation of a monitoring framework for a DevOps life-cycle based on semantic techniques and the OSLC standard

## Arquitecture


- Stackstorm y Kafka:

Se ha creado un script de bash para la inicialización de un ReplicaSet de MongoDB, añadiendo dos nodos secundarios al despliegue inicial de stackstorm en Docker. Por otro lado se ha incluido en el mismo docker-compose los servicios de zookeeper y kafka

- Módulo de monitorización

Archivo de Python que utiliza los change_stream de MongoDB para la monitorización activa de Stackstorm

- Graph Manager

Servidor flask estructurado con cookiecutter.

## Deploy and Test

Se está trabajando en un script que levante todo el escenario en un solo paso. De momento hay tres procesos que iniciar:

- Stackstorm y Kafka:

Primero hay que clonar el repositorio de Stackstorm para Docker [st2-docker](https://github.com/StackStorm/st2-docker). Una vez clonado, sustituir el docker-compose.yml del repositorio clonado, por el de la carpeta st2-docker-changes/.

Dentro de st2-docker-changes habrá dos scripts:

- start-st2.sh se encarga de levantar el escenario formado por un cluster replicaset con un nodo primario y dos secundarios, así como los servicios de zookeeper y kafka. Poner este archivo en la raiz del repo st2-docker recientemente clonado.
- rs-init.sh se ejecuta el iniciar el contenedor y permite la creacion del cluster replicaset de MongoDB. Meter este script en la carpeta st2-docker/mongo/rs-init.sh.


'''

./st2-docker/start-st2.sh

'''

- Módulo de monitorización

'''

python3 st2api/monitoring.py

'''

- Graph Manager

'''

flask run

'''

## Usage

Una vez desplegado todo el escenario se podrá acceder a Stackstorm en localhost.

Para interactuar con el graph manager se ha utilizado [Insomnia](https://insomnia.rest/) pero se puede hacer con otros clientes como curl. Todos los endpoints disponibles para recibir HTTP Requests están el /oslcapi/api/views.py. 
Cada endpoint está asociada a una función determinada

## Auth token for Stackstorm

- [Obtain an auth token for Stackstorm](https://docs.stackstorm.com/authentication.html)



## Project framework

Este trabajo se enmarca dentro del proyecto [SmartDevOps](https://smartdevops.gsi.upm.es) y pretende servir de demo para un caso de uso concreto. SmartDevOps desarrolla de manera mucho mas global los conceptos planteados en este trabajo.