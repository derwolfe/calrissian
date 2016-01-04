#!/bin/bash

exec docker run --rm -it \
     -p 8081:8081 \
     -p 8080:8080 \
     -e DH_PARAMETER $(cat ./dev_certs/dh2048.pem) \
     -e PRIVATE_KEY $(cat ./dev_certs/domain_dev.key) \
     -e CERTIFICATE_CHAIN $(cat ./dev_certs/domain_dev.cert) \
     -e SECURE_PORT 8181 \
     -e INSECURE_PORT 8080 \
     calrissian-run;
