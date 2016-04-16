#!/bin/sh

cd /etc/elastalert
elastalert-create-index --index "${ELASTALERT_INDEX}" --old-index ""
