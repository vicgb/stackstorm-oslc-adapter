# Stackstorm OSLC Adapter

***Trabajo Fin de Master: Design and implementation of a monitoring framework for a DevOps life-cycle based on semantic techniques and the OSLC standard.***

El adaptador Stackstorm-OSLC tiene dos partes fundamentales: 

- La primera idea es diseñar y desarrollar un framework de monitorización, basado en el estandar semántico OSLC, para las reglas de Stackstorm. Para ello se hará uso de OSLC Actions y OSLC Events (desarrollados bajo el marco del proyecto [SmartDevOps](https://smartdevops.gsi.upm.es)). Este framework será capaz de detectar cambios en las reglas (activación/desactivación, modificación y eliminación) y generar OSLC Events de manera automática. Estos eventos se enviarán a una instancia de Kafka para comunicación descentralizada.

- Por otro lado se pretende desarrollar un caso de uso concreto de un framework de integración de herramientas DevOps basado en eventos y acciones OSLC mediante el uso de Kafka. En este proyecto, el funcionamiento consiste en que para cada cambio producido en las reglas de Stackstorm (y detectado por el modulo de monitorización), el adaptador OSLC generará un grafo del tipo OSLC Event y se almacenará en Kafka bajo un topic. Una vez almacenado bajo el topic, otra herramienta (que tenga su respectivo adaptador OSLC) será capaz de suscribirse a ese topic y generar OSLC Actions de manera automática, ante cambios en las reglas de Stackstorm. De esta manera se construye un entorno automático de integración de herramientas DevOps basado en eventos y acciones OSLC.

Un diagrama general del adaptador stackstorm-OSLC sería:

![Image text](https://github.com/vicgb/stackstorm-oslc-adapter/blob/main/assets/diagrama_general.png)

Todos los módulos que forman la arquitectura se pueden encontrar en assets/. 

## Description
#### Stackstorm y Kafka:

Script de bash para la inicialización de un ReplicaSet de MongoDB, añadiendo dos nodos secundarios al despliegue inicial de Stackstorm en Docker. Por otro lado se ha incluido en el mismo docker-compose los servicios de Kafka y Zookeeper. La idea del docker-compose es que sea capaz de desplegar tanto el replicaset de MongoDB, como Kafka y Zookeeper, como Stackstorm.

#### Módulo de monitorización

Archivo de Python que utiliza los *change_stream* de MongoDB para la monitorización activa de Stackstorm. Es el módulo encargado de detectar cuando hay un cambio en alguna de las reglas de Stackstorm y generar un OSLC Event para enviarlo de manera automática a Kafka bajo el topic 'st2_event'. Se trata de un módulo de monitorización activa, es decir, no requiere de peticiones periódicas al endpoint de Stackstorm en busca de cambios si no que espera a recibir activamente los cambios producidos, en cuanto se producen.

#### Graph Manager

Servidor flask estructurado con Cookiecutter. Contiene en su archivo views.py todos los endpoints que recibirán HTTP requests para una función u otra. Estos endpoints podran recibir HTTP requests, llamarán a una determinada función y devolveran un grafo RDF con la respuesta. 

Por ejemplo, se puede consultar cuántas reglas hay en la instancia de Stackstorm mediante un HTTP GET a */serviceProviders/<int:service_provider_id>/changeRequests*. 


## Previous steps

#### Stackstorm y Kafka:

Primero hay que clonar el repositorio de Stackstorm para Docker [st2-docker](https://github.com/StackStorm/st2-docker). Una vez clonado, sustituir el docker-compose.yml del repositorio clonado, por el de la carpeta **st2-docker-changes/.**

Dentro de st2-docker-changes habrá dos scripts:

- **start-st2.sh**: Se encarga de levantar el escenario formado por un cluster replicaset con un nodo primario y dos secundarios, así como los servicios de zookeeper y kafka. Copiar este archivo en la raiz del repo st2-docker recientemente clonado.
- **rs-init.sh**: Se ejecuta el iniciar el contenedor y permite la creacion del cluster replicaset de MongoDB. Copiar este script en la carpeta *st2-docker/mongo/rs-init.sh*.


## Deploy and Test

Se puede iniciar todo el escenario, modificando paths y variables a su caso de uso, con la ejecución:

```
./deploy-scenario.sh
```

Con este script se arrancan los 3 procesos: Despliegue de escenario de Stackstorm y Kafka, inicio del proceso del módulo de monitorización e inicio del graph manager del adaptador Stackstorm-OSLC.

## Docker and Kubernetes Deploy

Se ha desplegado en Kubernetes desplegando la imagen utilizando el Registry privado de Gitlab, pero el procedimiento sería el mismo si se quiere hacer de manera pública:


```
docker login
docker build -t st2-oslc:<tag> .
docker push st2-oslc:<tag>
```

En el archivo k8s/st2-oslc.py hay que modificar el archivo env-secret.yaml, donde estarán las variables de entorno que se crearan como un secreto de Kubernetes:

```
kubectl create -f env-secret.yaml 
```

Y se crean el resto de recursos, como el deployment, el servicio y el ingress si se quiere.


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
- [Taiger](https://taiger.com)

## Project framework

Este trabajo se enmarca dentro del proyecto [SmartDevOps](https://smartdevops.gsi.upm.es), del [Grupo de Sistemas Inteligentes](https://gsi.upm.es) (UPM) y [Taiger](https://taiger.com). Pretende servir de demo para un caso de uso concreto. 

[SmartDevOps](https://smartdevops.gsi.upm.es) desarrolla de manera mucho mas global los conceptos planteados en este trabajo.

