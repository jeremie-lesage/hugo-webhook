# Hugo Webhook

This container provides a webhook that triggers a Hugo rebuild of a given git repository.

Based on [kramergroup/hugo-webhook](https://github.com/kramergroup/hugo-webhook), this webhook
image lets you authenticate to github, gitea or gitlab using a web token.

Some features:

* Web tokens: it is a lot easier to pass tokens as arguments to the chart than passing certificates.
* It doesn't make use of supervisord
* Smaller: it now uses the alpine docker image, webhook and hugo binaries have been compressed
  with UPX and thus the image is pretty small.
* It doesn't run as root.
* Can cache sources for faster pulling.

The container is meant to operate as a webhook consumer to trigger a rebuild of a
[Hugo](https://http://gohugo.io) static website. This can be used to automatically refresh a
static website after a git commit. A refresh is always triggered when the container is
started.

The container exposed a webhook listener on port 9000. A refresh of the site can be triggered with:

```bash
curl http://localhost:9000/hooks/refresh
```

The *hugo target directory* should be mounted by a static webserver (such as nginx) and served.
See the Kubernetes deployment example for a fully working deployment.

## Configuration

The container is configured through environment variables and some configuration files. The Hugo
version is 0.80.0.

### Environment variables

| Name                    | Description                                                                                         |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| `GIT_PROVIDER`          | Your git provider (GITHUB                                                                           |GITEA|GITLAB), defaults to GITHUB, only used if TRANSPORT is HTTP.       |
| `GIT_TRANSPORT`         | Whether to use SSH or HTTP git transport, defaults to HTTP.                                         |
| `GIT_HTTP_INSECURE`     | Force clear http as transport. (A nasty thing, you know what you're doing).                         |
| `GIT_REPO_URL`          | The URL of the git repository.                                                                      |
| `GIT_REPO_CONTENT_PATH` | The subpath of the repository holding the hugo source files (e.g., where `config.toml` is located). |
| `GIT_REPO_BRANCH`       | The branch of the git repository.                                                                   |
| `GIT_CLONE_DEST`        | Where to clone the repo to, defaults to /srv/src                                                    |
| `GIT_PRESERVE_SRC`      | Whether to preserve(cache) the src upon build or not. "TRUE" or "FALSE", default to FALSE           |
| `TARGET_DIR`            | Where to save hugo's built html, defaults to /srv/static                                            |
| `TARGET_SERVER_URI`     | /app                                                                                                |
| `TARGET_BASE_URL`       | https://my-server.app                                                                               |
| `BUILD_PARAMS`          | Additional HUGO/MKDOCS parameter (e.g., `--minify --gc`).                                           |
| `MATRIX_SERVER`         | Matrix server (ex. https://matrix.org)                                                              |
| `MATRIX_ROOM`           | Room to write to (ex. !roomid:matrix.org)                                                           |
| `MATRIX_TOKEN`          | Token use to connect to matrix server                                                               |

### Volumes and configuration files

| Name              | Description                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------|
| `/srv/static`     | The default location of the rendered HTML site.                                                                |
| `/etc/hooks.yaml` | The [webhook](https://github.com/adnanh/webhook) configuration file.                                           |
| `/ssh/id_rsa`     | The private key used to communicate with the git repository over SSH (needs to have at least 400 permissions). |

### GitLab Project Access Token

To clone a project hosted on GitLab, you need to create a **Project access token** with the following settings:

- **Role**: `Reporter`
- **Scope**: `read_repository`

When configuring authentication, use the **token name** as the username and the **token value** as the password.

# Deployment examples

## Docker

```bash
docker build -t jeci/hugo-webhook .

mkdir output
docker run --rm -it \
            -e GIT_REPO_URL=gitlab.com/pristy-oss/pristy-documentation.git/ \
            -e PROJECT_TYPE=mkdocs \
            -e GIT_REPO_BRANCH=staging \
            -p 9000:9000 \
            --user "$(id -u):$(id -g)" \
            -v ./output:/srv/static:rw \
            jeci/hugo-webhook
```

*NOTE*:
git repository url *should not* have the schema, ex: github.com/user/repo.git

This will run the container locally. A refresh can be triggered with

```bash
curl http://localhost:9000/hooks/mkdocs
```

## Kubernetes

Use this helm chart:

```
$ helm repo add jeci https://jeci.fr/helm-charts/
$ helm install jeci/hugo-webhook --set -e GIT_PROVIDER=GITHUB \
  --set GIT_REPO_URL=github.com/username/hugo-site.git
```

See [jfardello/hugo-webhook-chart](https://github.com/jfardello/hugo-webhook-chart).


## Build

```
docker build -t rg.fr-par.scw.cloud/jeci/hugo-webhook:0.8.0 .
docker push rg.fr-par.scw.cloud/jeci/hugo-webhook:0.8.0
```

