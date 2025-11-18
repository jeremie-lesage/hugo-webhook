FROM docker.io/library/alpine:3.22

ENV HUGO_VER=0.145.0
ENV WEBHOOK_VERSION=2.8.2
ENV MKDOCS_VERSION=1.6.1

# Configuration variables
ENV GIT_REPO_CONTENT_PATH=""
ENV GIT_CLONE_DEST=/srv/src
ENV GIT_REPO_BRANCH=master
ENV GIT_SSH_ID_FILE=/ssh/id_rsa
ENV TARGET_DIR=/srv/static

RUN addgroup -S app && \
    adduser -S -G app app  && \
    mkdir -p  /etc/webhook/ && \
    chown app:app /etc/webhook/  && \
    chmod 755 /etc/webhook/ && \
    apk add --update --no-cache \
        tzdata \
        ca-certificates \
        go \
        bash \
        git \
        npm \
        py3-regex \
        py3-pip \
        build-base && \
    update-ca-certificates && \
    pip install --break-system-packages \
                mkdocs==${MKDOCS_VERSION} \
                mkdocs-get-deps \
                mkdocs-git-authors-plugin \
                mkdocs-git-revision-date-localized-plugin \
                mkdocs-material \
                mkdocs-material-extensions \
                matrix_client

ENV HOME=/home/app

RUN --mount=type=cache,target=$HOME/go/pkg/mod \
    --mount=type=cache,target=$HOME/.cache/go-build \
    go install github.com/adnanh/webhook@${WEBHOOK_VERSION} && \
    mv /home/app/go/bin/webhook /usr/local/bin/ && \
    CGO_ENABLED=1 go install -tags extended github.com/gohugoio/hugo@v${HUGO_VER} && \
    mv /home/app/go/bin/hugo /usr/local/bin/

USER app

WORKDIR /srv

EXPOSE 9000
EXPOSE 80

COPY hooks.yaml /etc/webhook/hooks.yaml
COPY scripts /var/scripts

ENTRYPOINT ["/usr/local/bin/webhook", "-verbose", "-hooks", "/etc/webhook/hooks.yaml"]
