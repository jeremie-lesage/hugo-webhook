FROM        docker.io/library/alpine:3.20

ENV WEBHOOK_VERSION=2.8.1

# Configuration variables
ENV GIT_REPO_CONTENT_PATH=""
ENV GIT_CLONE_DEST=/srv/src
ENV GIT_USERNAME=foo_user
ENV GIT_REPO_BRANCH=master
ENV GIT_SSH_ID_FILE=/ssh/id_rsa
ENV TARGET_DIR=/srv/static

RUN addgroup -S app && \
    adduser -S -G app app  && \
    mkdir -p ${TARGET_DIR} ${GIT_CLONE_DEST} /etc/webhook/ && \
    chown app:app ${TARGET_DIR} ${GIT_CLONE_DEST} /etc/webhook/  && \
    chmod 755 ${TARGET_DIR} ${GIT_CLONE_DEST} /etc/webhook/ && \
    apk add --update --no-cache \
        go \
        bash \
        git \
        hugo \
        mkdocs-material-extensions \
        mkdocs-material \
        mkdocs \
        py3-regex


ENV HOME=/home/app

RUN --mount=type=cache,target=$HOME/go/pkg/mod \
    --mount=type=cache,target=$HOME/.cache/go-build \
    go install github.com/adnanh/webhook@${WEBHOOK_VERSION}

USER app

WORKDIR ${GIT_CLONE_DEST}

EXPOSE 9000
EXPOSE 80

COPY hooks.yaml /etc/webhook/hooks.yaml
COPY scripts /var/scripts

ENTRYPOINT ["/home/app/go/bin/webhook", "-verbose", "-hooks", "/etc/webhook/hooks.yaml"]
