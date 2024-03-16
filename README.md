# Sidecar docker image

This repository builds the docker image for the k-pipe sidecar container, which accompanies the main payload container
of pods (created by the kubernetes jobs that are processing the k-pipe steps).

## Functionality

The sidecar container is responsible for downloading the required input files before the main container starts and
uploading the output files when the main container has terminated. Besides that, it can optionally monitor the pod's 
resource consumption.

### Exchange of information 

The sidecar and main container both mount a common volume `\workdir` which is used to exchange information. This 
volume is initialized empty and populated with the following files as part of the execution process of a k-pipe pod:

| File                    | Created by | Function                                                                                                                                                                                                     |
|-------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/workdir/input/*`      | sidecar    | input files required by the main container                                                                                                                                                                   |
| `/workdir/output/*`     | main       | output files produced by the main container                                                                                                                                                                  |
| `/workdir/ready`        | sidecar    | indicates to kubernetes that the sidecar has finished initialization and the main container can start                                                                                                        |
| `/workdir/healthy`      | main       | this file is regularly deleted by the kubernetes healthiness probe and must be re-created by the main container within a certain deadline, otherwise the pod will be considered unhealthy                    |
| `/workdir/started`      | kubernetes | this file is created by kubernetes when the main container is started, it is monitored by the sidecar to update the state in the backend                                                                     |
| `/workdir/state`        | main       | this file contains one line of text which encodes the state of the main container (e.g. RUNNING, SUCCESS, ERROR, KILLED or custom values), it is monitored by the sidecar to update the state in the backend |
| `/workdir/done`         | main       | this file is created by the main container to indicate that processing is done and the main container is about to terminate                                                                                  |
| `/workdir/output/log`   | main       | this file contains the logs (standard output) produced by the processing payload running inside the main container                                                                                           |
| `/workdir/output/error` | main       | this file contains the errors (error output) produced by the processing payload running inside the main container                                                                                            |

### Regular lifecycle of a k-pipe job pod

If a k-pipe job is executed successfully, the corresponding pod passes through the following stages:

| Stage       | Kubernetes action                               | Sidecar container action                     | Main container action                     |
|-------------|-------------------------------------------------|----------------------------------------------|-------------------------------------------|
| PENDING     | scales up nodes and schedules pod for execution |                                              |                                           | 
|             | starts sidecar container                        |                                              |                                           |
| INTIALIZING |                                                 | updates backend state to `INITIALIZING`      |                                           |
|             |                                                 | downloads input files into `/workdir/inputs` |                                           |
|             |                                                 | creates `/workdir/ready`                     |                                           |
|             | starts main container                           |                                              |                                           |
|             | creates file `/workdir/started`                 |                                              |                                           |
| STARTED     |                                                 | updates backend state to `STARTED`           |                                           |
|             |                                                 |                                              | creates `/workdir/state` with `RUNNING`   |
| RUNNING     |                                                 | updates backend state to `RUNNING`           |                                           |
|             |                                                 |                                              | executes processing payload               |
|             |                                                 |                                              | reads files in `/workdir/input/`          |
|             |                                                 |                                              | updates `/workdir/state` to custom values |
| *           |                                                 | updates backend state accordingly            |                                           |
|             |                                                 |                                              | creates files in `/workdir/output/`       |
|             |                                                 | uploads files (optionally)                   |                                           |
|             |                                                 |                                              | creates file `/workdir/done`              |
|             |                                                 |                                              | terminates                                |
| TERMINATING |                                                 | updates backend state to `TERMINATING`       |                                           |
|             |                                                 | uploads files (if not yet done before)       |                                           |
| DONE        |                                                 | updates backend state to `DONE`              |                                           |
|             | shuts down the pod                              |                                              |                                           |

## Building

## References
