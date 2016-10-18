##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
# bulk data test and req/rsp test are supported
import pkg_resources
import logging
import json

import yardstick.ssh as ssh
from yardstick.benchmark.scenarios import base

LOG = logging.getLogger(__name__)


class NetperfNode(base.Scenario):
    """Execute netperf between two nodes

  Parameters
    testname - to specify the test you wish to perform.
    the valid testnames are TCP_STREAM, TCP_RR, UDP_STREAM, UDP_RR
        type:    string
        unit:    na
        default: TCP_STREAM
    send_msg_size - value set the local send size to value bytes.
        type:    int
        unit:    bytes
        default: na
    recv_msg_size - setting the receive size for the remote system.
        type:    int
        unit:    bytes
        default: na
    req_rsp_size - set the request and/or response sizes based on sizespec.
        type:    string
        unit:    na
        default: na
    duration - duration of the test
        type:    int
        unit:    seconds
        default: 20

    read link below for more netperf args description:
    http://www.netperf.org/netperf/training/Netperf.html
    """
    __scenario_type__ = "NetperfNode"
    TARGET_SCRIPT = 'netperf_benchmark.bash'
    INSTALL_SCRIPT = 'netperf_install.bash'
    REMOVE_SCRIPT = 'netperf_remove.bash'

    def __init__(self, scenario_cfg, context_cfg):
        self.scenario_cfg = scenario_cfg
        self.context_cfg = context_cfg
        self.setup_done = False

    def setup(self):
        '''scenario setup'''
        self.target_script = pkg_resources.resource_filename(
            'yardstick.benchmark.scenarios.networking',
            NetperfNode.TARGET_SCRIPT)
        host = self.context_cfg['host']
        host_user = host.get('user', 'ubuntu')
        host_ip = host.get('ip', None)
        target = self.context_cfg['target']
        target_user = target.get('user', 'ubuntu')
        target_ip = target.get('ip', None)
        self.target_ip = target.get('ip', None)
        host_password = host.get('password', None)
        target_password = target.get('password', None)
        key_dir = pkg_resources.resource_filename(
                    'yardstick.resources.files', 'yardstick_key')
        if target_password is not None:
            LOG.debug("Log in via pw, user:%s, host:%s, password:%s",
                      target_user, target_ip, target_password)
            self.server = ssh.SSH(target_user, target_ip,
                                  password=target_password)
        else:
            target_keyfile = target.get('key_filename', key_dir)
            LOG.debug("Log in via key, user:%s, host:%s, key_filename:%s",
                      target_user, target_ip, target_keyfile)
            self.server = ssh.SSH(target_user, target_ip,
                                  key_filename=target_keyfile)
        self.server.wait(timeout=60)

        if host_password is not None:
            LOG.debug("Log in via pw, user:%s, host:%s, password:%s",
                      host_user, host_ip, host_password)
            self.client = ssh.SSH(host_user, host_ip,
                                  password=host_password)
        else:
            host_keyfile = target.get('key_filename', key_dir)
            LOG.debug("Log in via key, user:%s, host:%s, key_filename:%s",
                      host_user, host_ip, host_keyfile)
            self.client = ssh.SSH(host_user, host_ip,
                                  key_filename=host_keyfile)
        self.client.wait(timeout=60)

        # copy script to host
        self.client.run("cat > ~/netperf.sh",
                        stdin=open(self.target_script, "rb"))

        # copy script to host and client
        self.install_script = pkg_resources.resource_filename(
            'yardstick.benchmark.scenarios.networking',
            NetperfNode.INSTALL_SCRIPT)
        self.remove_script = pkg_resources.resource_filename(
            'yardstick.benchmark.scenarios.networking',
            NetperfNode.REMOVE_SCRIPT)

        self.server.run("cat > ~/netperf_install.sh",
                        stdin=open(self.install_script, "rb"))
        self.client.run("cat > ~/netperf_install.sh",
                        stdin=open(self.install_script, "rb"))
        self.server.run("cat > ~/netperf_remove.sh",
                        stdin=open(self.remove_script, "rb"))
        self.client.run("cat > ~/netperf_remove.sh",
                        stdin=open(self.remove_script, "rb"))
        self.server.execute("sudo bash netperf_install.sh")
        self.client.execute("sudo bash netperf_install.sh")

        self.setup_done = True

    def run(self, result):
        """execute the benchmark"""

        if not self.setup_done:
            self.setup()

        # get global options
        ipaddr = self.context_cfg['target'].get("ipaddr", '127.0.0.1')
        ipaddr = self.target_ip
        options = self.scenario_cfg['options']
        testname = options.get("testname", 'TCP_STREAM')
        duration_time = self.scenario_cfg["runner"].get("duration", None) \
            if "runner" in self.scenario_cfg else None
        arithmetic_time = options.get("duration", None)
        if duration_time:
            testlen = duration_time
        elif arithmetic_time:
            testlen = arithmetic_time
        else:
            testlen = 20

        cmd_args = "-H %s -l %s -t %s -c -C" % (ipaddr, testlen, testname)

        # get test specific options
        output_opt = options.get("output_opt", None)
        default_args = "-O %s" % output_opt
        cmd_args += " -- %s" % default_args
        option_pair_list = [("send_msg_size", "-m"),
                            ("recv_msg_size", "-M"),
                            ("send_cache_size", "-s"),
                            ("recv_cache_size", "-S"),
                            ("req_rsp_size", "-r")]
        for option_pair in option_pair_list:
            if option_pair[0] in options:
                cmd_args += " %s %s" % (option_pair[1],
                                        options[option_pair[0]])

        cmd = "sudo bash netperf.sh %s" % (cmd_args)
        LOG.debug("Executing command: %s", cmd)
        status, stdout, stderr = self.client.execute(cmd)

        if status:
            raise RuntimeError(stderr)

        result.update(json.loads(stdout))
        print result
        LOG.debug("Result: %s", stdout)

    def teardown(self):
        '''remove netperf from nodes after test'''
        self.server.execute("sudo bash netperf_remove.sh")
        self.client.execute("sudo bash netperf_remove.sh")


def _test():    # pragma: no cover
    '''internal test function'''
    ctx = {
        "host": {
            "ip": "192.168.10.10",
            "user": "root",
            "password": "root"
        },
        "target": {
            "ip": "192.168.10.11",
            "user": "root",
            "password": "root"
        }
    }

    logger = logging.getLogger("yardstick")
    logger.setLevel(logging.DEBUG)

    options = {
        "testname": 'TCP_STREAM'
    }

    args = {"options": options}
    result = {}

    netperf = NetperfNode(args, ctx)
    netperf.run(result)
    print result

if __name__ == '__main__':
    _test()
