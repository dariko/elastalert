FROM python:2.7.11-alpine

ENV ELASTALERT_VERSION 0.0.77
ENV ELASTALERT_URL https://github.com/Yelp/elastalert/archive/v${ELASTALERT_VERSION}.tar.gz
ENV ELASTALERT_DIRECTORY /opt/elastalert-${ELASTALERT_VERSION}
ENV ELASTALERT_CONFIG /etc/elastalert/config.yml

RUN apk add --no-cache openssl ca-certificates python-dev gcc musl-dev \
    && mkdir -p "$(dirname ${ELASTALERT_CONFIG})" \
    && mkdir -p "$(dirname ${ELASTALERT_DIRECTORY})" \
    && wget -O - "${ELASTALERT_URL}" | tar xzC "$(dirname ${ELASTALERT_DIRECTORY})" \
    && ls -la /opt \
    && cd "${ELASTALERT_DIRECTORY}" \
    && pip install -r requirements.txt \
    && python setup.py install \
    && apk del python-dev musl-dev gcc \
    && true

CMD ["elastalert", "--config", "${ELASTALERT_CONFIG}"]
