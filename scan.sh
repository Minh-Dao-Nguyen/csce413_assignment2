#!/bin/bash

docker run --rm -it \
  --network csce413_assignment2_vulnerable_network \
  port-scanner \
  "$@"
