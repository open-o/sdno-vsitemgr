#!/bin/bash
#
#  Copyright 2016-2017 China Telecommunication Co., Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

MSB_ADDRESS="msb.openo.org:8086"
SDNO_SDNO_VSITEMGR_ADDRESS="sdno-vsitemgr:8600"

PROC_UNIQ_KEY=0c54be48-73da-49bd-917b-e3a3853e3285
BASEDIR=$(dirname $(readlink -f $0))

OPTS=""
OPTS+=" --uniq=${PROC_UNIQ_KEY}"
OPTS+=" --msburl=${MSB_ADDRESS}"
OPTS+=" --localurl=${SDNO_SDNO_VSITEMGR_ADDRESS}"

if [ "$CSIT" == "True" ]; then 
    nohup coverage run --parallel-mode ${BASEDIR}/customer_serv.py ${OPTS} &> /dev/null &
    nohup coverage run --parallel-mode ${BASEDIR}/customer_server.py ${OPTS} &> /dev/null &
    nohup python ${BASEDIR}/test.py ${OPTS}  &
else
    nohup python ${BASEDIR}/customer_serv.py ${OPTS} &> /dev/null &
    nohup python ${BASEDIR}/customer_server.py ${OPTS} &> /dev/null &
fi
