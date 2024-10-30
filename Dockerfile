FROM docker.io/library/alpine:3.20

ENV WEBHOOK_VERSION=2.8.1
ENV MKDOCS_VERSION=1.6.1

# Configuration variables
ENV GIT_REPO_CONTENT_PATH=""
ENV GIT_CLONE_DEST=/srv/src
ENV GIT_USERNAME="nologin"
ENV GIT_REPO_BRANCH=master
ENV GIT_SSH_ID_FILE=/ssh/id_rsa
ENV TARGET_DIR=/srv/static

RUN addgroup -S app && \
    adduser -S -G app app  && \
    mkdir -p  /etc/webhook/ && \
    chown app:app /etc/webhook/  && \
    chmod 755 /etc/webhook/ && \
    apk add --update --no-cache \
        ca-certificates \
        go \
        bash \
        git \
        hugo \
        py3-regex \
        py3-pip \
        build-base && \
    pip install --break-system-packages \
                mkdocs==${MKDOCS_VERSION} \
                mkdocs-get-deps \
                mkdocs-git-authors-plugin \
                mkdocs-git-revision-date-localized-plugin \
                mkdocs-material \
                mkdocs-material-extensions


ENV HOME=/home/app

RUN --mount=type=cache,target=$HOME/go/pkg/mod \
    --mount=type=cache,target=$HOME/.cache/go-build \
    go install github.com/adnanh/webhook@${WEBHOOK_VERSION}

USER app

WORKDIR /srv

EXPOSE 9000
EXPOSE 80

COPY hooks.yaml /etc/webhook/hooks.yaml
COPY scripts /var/scripts

ENTRYPOINT ["/home/app/go/bin/webhook", "-verbose", "-hooks", "/etc/webhook/hooks.yaml"]
