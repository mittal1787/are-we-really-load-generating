#!/bin/sh

set -x
for vm in $(cat machines)
do
    ssh yugm2@$vm "${@:1}"
done
set +x