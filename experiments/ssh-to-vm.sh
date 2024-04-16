#!/bin/sh

set -x
for vm in $(cat machines)
do
    ssh <your-netid-here>@$vm "${@:1}"
done
set +x