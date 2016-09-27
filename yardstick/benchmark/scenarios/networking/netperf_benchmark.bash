#!/bin/bash

##############################################################################
# Copyright (c) 2015 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -e

# Commandline arguments
OPTIONS="$*"
OUTPUT_FILE=/tmp/netperf-out.log

# run netperf test
run_netperf()
{
    netperf $OPTIONS -O "THROUGHPUT, MEAN_LATENCY, LOCAL_CPU_UTIL, REMOTE_CPU_UTIL, LOCAL_SEND_SIZE, LOCAL_TRANSPORT_RETRANS" > $OUTPUT_FILE
}

# write the result to stdout in json format
output_json()
{
    thoughtoutput=$(sed -n '$p' $OUTPUT_FILE | awk '{print $1}')
    mean_lantcy=$(sed -n '$p' $OUTPUT_FILE | awk '{print $2}')
    local_cpu_locd=$(sed -n '$p' $OUTPUT_FILE | awk '{print $3}')
    remote_cpu_load=$(sed -n '$p' $OUTPUT_FILE | awk '{print $4}')
    local_tran_retran=$(sed -n '$p' $OUTPUT_FILE | awk '{print $5}')    
    echo -e "{ \
        \"troughput\":\"$thoughtoutput\", \
        \"mean_latency\":\"$mean_lantcy\", \
        \"local_cpu_load\":\"$local_cpu_locd\", \
        \"remote_cpu_load\":\"$remote_cpu_load\", \
        \"local_tran_retran\":\"$local_tran_retran\" \
    }"
}

# main entry
main()
{
    # run the test
    run_netperf

    # output result
    output_json
}

main
