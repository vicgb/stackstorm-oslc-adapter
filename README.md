# Stackstorm OSLC Adapter

Trabajo Fin de Master: Design and implementation of a monitoring framework for a DevOps life-cycle based on semantic techniques and the OSLC standard.

La idea de este proyecto es diseñar y desarrollar un framework de monitorización de Stackstorm mediante la estandarización semántica con OSLC. Se podrá interactuar con el Graph Manager del adaptador mediante peticiones HTTP a los endpoints de /views.py y se podrá ver el modelado semántico, siguiendo los requisitos del CORE de OSLC, que se ha realizado de las reglas de Stackstorm. Por otro lado se pretende desarrollar un framework de integración de herramientas DevOps basado en eventos y acciones mediante el uso de Kafka para comunicación descentralizada. 

Para cada acción producida en las reglas de Stackstorm, el adaptador generará un grafo del tipo OSLC Event y se almacenará en Kafka bajo un topic. El resto de herramientas DevOps que tengan su propio adaptador OSLC podrán suscribirse a este topic para realizar OSLC Actions de manera automatizada. Esto último queda fuera de los márgenes del proyecto y se enmarca dentro de SmartDevOps. 

## Arquitecture


- Stackstorm y Kafka:

Script de bash para la inicialización de un ReplicaSet de MongoDB, añadiendo dos nodos secundarios al despliegue inicial de stackstorm en Docker. Por otro lado se ha incluido en el mismo docker-compose los servicios de Kafka y Zookeeper.

- Módulo de monitorización

Archivo de Python que utiliza los change_stream de MongoDB para la monitorización activa de Stackstorm.

- Graph Manager

Servidor flask estructurado con cookiecutter. Contiene en su archivo views.py todos los endpoints que recibirán HTTP requests para una función u otra. 

## Previous steps

- Stackstorm y Kafka:

Primero hay que clonar el repositorio de Stackstorm para Docker [st2-docker](https://github.com/StackStorm/st2-docker). Una vez clonado, sustituir el docker-compose.yml del repositorio clonado, por el de la carpeta st2-docker-changes/.

Dentro de st2-docker-changes habrá dos scripts:

- start-st2.sh: Se encarga de levantar el escenario formado por un cluster replicaset con un nodo primario y dos secundarios, así como los servicios de zookeeper y kafka. Copiar este archivo en la raiz del repo st2-docker recientemente clonado.
- rs-init.sh: Se ejecuta el iniciar el contenedor y permite la creacion del cluster replicaset de MongoDB. Copiar este script en la carpeta st2-docker/mongo/rs-init.sh.

## Deploy and Test

Se puede iniciar todo el escenario, modificando paths y variables a su caso de uso, con la ejecución:

```
./deploy-scenario.sh
```

Con este script se arrancan los 3 procesos: Despliegue de escenario de Stackstorm y Kafka, inicio del proceso del módulo de monitorización e inicio del graph manager del adaptador Stackstorm-OSLC.

## Usage

Una vez desplegado todo el escenario se podrá acceder a Stackstorm en localhost, para crear/eliminar/modificar reglas. El modulo de monitorización está pensado para reaccionar ante eventos en las reglas(activación/desactivación, modificación y eliminación) y pretende servir de guía para futuras estandarizaciones OSLC de otros componentes de Stackstorm.

Para interactuar con el Graph Manager del adaptador se recomienda [Insomnia](https://insomnia.rest/) pero se puede hacer con otros clientes como [curl](https://www.solvetic.com/tutoriales/article/8011-como-instalar-curl-en-linux/). El adaptador permite la recepción de HTTP Requests (GET,POST,PUT) para actuar directamente contra Stackstorm, así como para consultar las reglas de Stackstorm como recursos OSLC.

Por otro lado, se podrá consultar el ChangeLog con todos los eventos producidos en Stackstorm mediante una peticion GET al TRS.

Todos los endpoints disponibles para recibir HTTP Requests están en /oslcapi/api/views.py. 
Cada endpoint está asociada a una función determinada.

Hay un ejemplo del body a incluir en el POST del endpoint de las actions/ para realizar cualquier acción contra las reglas de Stackstorm desde el adaptador. 

```
Headers: 
- Content-Type: application/rdf+xml
- Accept: application/rdf+xml
```

## Auth token for Stackstorm

- [Obtain an auth token for Stackstorm](https://docs.stackstorm.com/authentication.html)


## Links of interest

- [OSLC-PRIMER](https://open-services.net/resources/oslc-primer/)
- [OSLC-CORE](https://archive.open-services.net/bin/view/Main/OslcCoreSpecification)
- [RDF](https://www.w3.org/TR/rdf-primer/)
- [Stackstorm-API](https://api.stackstorm.com/)
- [SmartDevOps](https://smartdevops.gsi.upm.es)
- [GSI](https://gsi.upm.es)

## Project framework

Este trabajo se enmarca dentro del proyecto [SmartDevOps](https://smartdevops.gsi.upm.es) y pretende servir de demo para un caso de uso concreto. SmartDevOps desarrolla de manera mucho mas global los conceptos planteados en este trabajo.
Todas las métricas sociales del proyecto se pueden encontrar en el siguiente [Dashboard](https://dashboard-smartdevops.gsi.upm.es)
