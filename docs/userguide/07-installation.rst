.. This work is licensed under a Creative Commons Attribution 4.0 International
.. License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Ericsson AB, Huawei Technologies Co.,Ltd and others.

Yardstick Installation
======================

Abstract
--------

Yardstick currently supports installation on Ubuntu 14.04 or by using a Docker
image. Detailed steps about installing Yardstick using both of these options
can be found below.

To use Yardstick you should have access to an OpenStack environment,
with at least Nova, Neutron, Glance, Keystone and Heat installed.

The steps needed to run Yardstick are:

1. Install Yardstick and create the test configuration .yaml file.
2. Build a guest image and load the image into the OpenStack environment.
3. Create a Neutron external network and load OpenStack environment variables.
4. Run the test case.


Installing Yardstick on Ubuntu 14.04
------------------------------------

.. _install-framework:

Installing Yardstick framework
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install dependencies:
::

  sudo apt-get update && sudo apt-get install -y \
      wget \
      git \
      sshpass \
      qemu-utils \
      kpartx \
      libffi-dev \
      libssl-dev \
      python \
      python-dev \
      python-virtualenv \
      libxml2-dev \
      libxslt1-dev \
      python-setuptools

Create a python virtual environment, source it and update setuptools:
::

  virtualenv ~/yardstick_venv
  source ~/yardstick_venv/bin/activate
  easy_install -U setuptools

Download source code and install python dependencies:
::

  git clone https://gerrit.opnfv.org/gerrit/yardstick
  cd yardstick
  python setup.py install

There is also a YouTube video, showing the above steps:

.. image:: http://img.youtube.com/vi/4S4izNolmR0/0.jpg
   :alt: http://www.youtube.com/watch?v=4S4izNolmR0
   :target: http://www.youtube.com/watch?v=4S4izNolmR0

Installing extra tools
^^^^^^^^^^^^^^^^^^^^^^
yardstick-plot
""""""""""""""
Yardstick has an internal plotting tool ``yardstick-plot``, which can be installed
using the following command:
::

  sudo apt-get install -y g++ libfreetype6-dev libpng-dev pkg-config
  python setup.py develop easy_install yardstick[plot]

.. _guest-image:

Building a guest image
^^^^^^^^^^^^^^^^^^^^^^
Yardstick has a tool for building an Ubuntu Cloud Server image containing all
the required tools to run test cases supported by Yardstick. It is necessary to
have sudo rights to use this tool.

Also you may need install several additional packages to use this tool, by
follwing the commands below:
::

  apt-get update && apt-get install -y \
      qemu-utils \
      kpartx

This image can be built using the following command while in the directory where
Yardstick is installed (``~/yardstick`` if the framework is installed
by following the commands above):
::

  sudo ./tools/yardstick-img-modify tools/ubuntu-server-cloudimg-modify.sh

**Warning:** the script will create files by default in:
``/tmp/workspace/yardstick`` and the files will be owned by root!

The created image can be added to OpenStack using the ``glance image-create`` or
via the OpenStack Dashboard.

Example command:
::

  glance --os-image-api-version 1 image-create \
  --name yardstick-trusty-server --is-public true \
  --disk-format qcow2 --container-format bare \
  --file /tmp/workspace/yardstick/yardstick-trusty-server.img


Installing Yardstick using Docker
---------------------------------

Yardstick has two Docker images, first one (**Yardstick-framework**) serves as a
replacement for installing the Yardstick framework in a virtual environment (for
example as done in :ref:`install-framework`), while the other image is mostly for
CI purposes (**Yardstick-CI**).

Yardstick-framework image
^^^^^^^^^^^^^^^^^^^^^^^^^
Download the source code:

::

  git clone https://gerrit.opnfv.org/gerrit/yardstick

Build the Docker image and tag it as *yardstick-framework*:

::

  cd yardstick
  docker build -t yardstick-framework .

Run the Docker instance:

::

  docker run --name yardstick_instance -i -t yardstick-framework

To build a guest image for Yardstick, see :ref:`guest-image`.

Yardstick-CI image
^^^^^^^^^^^^^^^^^^
Pull the Yardstick-CI Docker image from Docker hub:

::

  docker pull opnfv/yardstick:$DOCKER_TAG

Where ``$DOCKER_TAG`` is latest for master branch, as for the release branches,
this coincides with its release name, such as brahmaputra.1.0.

Run the Docker image:

::

  docker run \
   --privileged=true \
    --rm \
    -t \
    -e "INSTALLER_TYPE=${INSTALLER_TYPE}" \
    -e "INSTALLER_IP=${INSTALLER_IP}" \
    opnfv/yardstick \
    exec_tests.sh ${YARDSTICK_DB_BACKEND} ${YARDSTICK_SUITE_NAME}

Where ``${INSTALLER_TYPE}`` can be apex, compass, fuel or joid, ``${INSTALLER_IP}``
is the installer master node IP address (i.e. 10.20.0.2 is default for fuel). ``${YARDSTICK_DB_BACKEND}``
is the IP and port number of DB, ``${YARDSTICK_SUITE_NAME}`` is the test suite you want to run.
For more details, please refer to the Jenkins job defined in Releng project, labconfig information
and sshkey are required. See the link
https://git.opnfv.org/cgit/releng/tree/jjb/yardstick/yardstick-ci-jobs.yml.

Note: exec_tests.sh is used for executing test suite here, furthermore, if someone wants to execute the
test suite manually, it can be used as long as the parameters are configured correct. Another script
called run_tests.sh is used for unittest in Jenkins verify job, in local manaul environment,
it is recommended to run before test suite execuation.

Basic steps performed by the **Yardstick-CI** container:

1. clone yardstick and releng repos
2. setup OS credentials (releng scripts)
3. install yardstick and dependencies
4. build yardstick cloud image and upload it to glance
5. upload cirros-0.3.3 cloud image to glance
6. run yardstick test scenarios
7. cleanup


OpenStack parameters and credentials
------------------------------------

Yardstick-flavor
^^^^^^^^^^^^^^^^
Most of the sample test cases in Yardstick are using an OpenStack flavor called
*yardstick-flavor* which deviates from the OpenStack standard m1.tiny flavor by the
disk size - instead of 1GB it has 3GB. Other parameters are the same as in m1.tiny.

Environment variables
^^^^^^^^^^^^^^^^^^^^^
Before running Yardstick it is necessary to export OpenStack environment variables
from the OpenStack *openrc* file (using the ``source`` command) and export the
external network name ``export EXTERNAL_NETWORK="external-network-name"``,
the default name for the external network is ``net04_ext``.

Credential environment variables in the *openrc* file have to include at least:

* OS_AUTH_URL
* OS_USERNAME
* OS_PASSWORD
* OS_TENANT_NAME

Yardstick default key pair
^^^^^^^^^^^^^^^^^^^^^^^^^^
Yardstick uses a SSH key pair to connect to the guest image. This key pair can
be found in the ``resources/files`` directory. To run the ``ping-hot.yaml`` test
sample, this key pair needs to be imported to the OpenStack environment.


Examples and verifying the install
----------------------------------

It is recommended to verify that Yardstick was installed successfully
by executing some simple commands and test samples. Below is an example invocation
of yardstick help command and ping.py test sample:
::

  yardstick –h
  yardstick task start samples/ping.yaml

Each testing tool supported by Yardstick has a sample configuration file.
These configuration files can be found in the **samples** directory.

Example invocation of ``yardstick-plot`` tool:
::

  yardstick-plot -i /tmp/yardstick.out -o /tmp/plots/

Default location for the output is ``/tmp/yardstick.out``.

More info about the tool can be found by executing:
::

  yardstick-plot -h


Deploy InfluxDB and Grafana locally
------------------------------------

.. pull docker images

Pull docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  docker pull tutum/influxdb
  docker pull grafana/grafana

Run influxdb and config
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run influxdb
::

  docker run -d --name influxdb \
  -p 8083:8083 -p 8086:8086 --expose 8090 --expose 8099 \
  tutum/influxdb
  docker exec -it influxdb bash

Config influxdb
::

  influx
  >CREATE USER root WITH PASSWORD 'root' WITH ALL PRIVILEGES
  >CREATE DATABASE yardstick;
  >use yardstick;
  >show MEASUREMENTS;

Run grafana and config
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run grafana
::

  docker run -d --name grafana -p 3000:3000 grafana/grafana

Config grafana
::

  http://{YOUR_IP_HERE}:3000
  log on using admin/admin and config database resource to be {YOUR_IP_HERE}:8086

.. image:: images/Grafana_config.png

Config yardstick conf
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cp ./etc/yardstick/yardstick.conf.sample /etc/yardstick/yardstick.conf

vi /etc/yardstick/yardstick.conf
Config yardstick.conf
::

  [DEFAULT]
  debug = True
  dispatcher = influxdb

  [dispatcher_influxdb]
  timeout = 5
  target = http://{YOUR_IP_HERE}:8086
  db_name = yardstick
  username = root
  password = root

Now you can run yardstick test case and store the results in influxdb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Create a test suite for yardstick
------------------------------------

A test suite in yardstick is a yaml file which include one or more test cases.
Yardstick is able to support running test suite task, so you can customize you
own test suite and run it in one task.

"tests/opnfv/test_suites" is where yardstick put ci test-suite. A typical test
suite is like below:

fuel_test_suite.yaml

::

  ---
  # Fuel integration test task suite

  schema: "yardstick:suite:0.1"

  name: "fuel_test_suite"
  test_cases_dir: "samples/"
  test_cases:
  -
    file_name: ping.yaml
  -
    file_name: iperf3.yaml

As you can see, there are two test cases in fuel_test_suite, the syntas is simple
here, you must specify the schema and the name, then you just need to list the
test cases in the tag "test_cases" and also mark their relative directory in the
tag "test_cases_dir".

Yardstick test suite also support constraints and task args for each test suite.
Here is another sample to show this, which is digested from one big test suite.

os-nosdn-nofeature-ha.yaml

::

 ---

 schema: "yardstick:suite:0.1"

 name: "os-nosdn-nofeature-ha"
 test_cases_dir: "tests/opnfv/test_cases/"
 test_cases:
 -
     file_name: opnfv_yardstick_tc002.yaml
 -
     file_name: opnfv_yardstick_tc005.yaml
 -
     file_name: opnfv_yardstick_tc043.yaml
        constraint:
           installer: compass
           pod: huawei-pod1
        task_args:
           huawei-pod1: '{"pod_info": "etc/yardstick/.../pod.yaml",
           "host": "node4.LF","target": "node5.LF"}'

As you can see in test case "opnfv_yardstick_tc043.yaml", it has two tags, "constraint" and
"task_args". "constraint" is where you can specify which installer or pod it can be run in
the ci environment. "task_args" is where you can specify the task arguments for each pod.

All in all, to create a test suite in yardstick, you just need to create a suite yaml file
and add test cases and constraint or task arguments if necessary.
