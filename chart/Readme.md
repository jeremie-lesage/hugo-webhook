# Hugo-webhook

## Introduction

This chart deploys a webhook that builds Hugo sites (or Mkdocs) from git sources and hosts the generated site with an
nginx container on the same pod.
It supports git clone/pull via http with web tokens as well as via ssh with certificates.

## Prerequisites

* A kubernetes cluster >=1.14
* The helm client

# Installing the chart

This chart is published in jeci/charts. To install the chart, first add the helm repo:

``helm repo add jeci https://jeci.fr/charts/``

Then install the release:

``helm install jeci jeci/hugo-webhook -f values.yaml``

Now if you provided an ingress you should call https://ingress.tld/hooks/refresh to build the site

> :warning: **The sample webhook deployed is public and not secured**, anyone having access to the URL will be able to
> trigger builds, its up to you to secure it by editing the rules
>
configmap, [by looking for a github/gitlab known secret](https://github.com/adnanh/webhook/blob/master/docs/Hook-Examples.md).

Sample config for a traefik ingres:

```yaml
git:
  provider: "GITEA"
  transport: "HTTP"
  token: "sampletoken-aaaabbbbccc"
  username: "jfardello"
  repoUrl: git.domain.tld/foouser/foo-docs
  repoContentPath: "ktdocs"
  repoBranch: "master"
  cloneDest: "/srv/src"
  target_dir: "/srv/static"
  preserveSrc: "TRUE"

hugo:
  params: --minify

ingress:
  traefikTls: true
  enabled: true
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.tls.certresolver: resolver007
    traefik.ingress.kubernetes.io/router.tls.domains.0.main: '*.domain.tld'
  hosts:
    - host: docs.kubewire.net
```

## Configuration

The following table lists the configurable parameters of the Hugo-webhook chart and their default values.

| Parameter                         | Description                                                               | Default                               |
|-----------------------------------|---------------------------------------------------------------------------|---------------------------------------|
| `replicaCount`                    |                                                                           | `1`                                   |
| `image.nginxRepository`           | Nginx image                                                               | `"nginx"`                             |
| `image.nginxVersion`              | Image tag for the nginx image                                             | `"latest"`                            |
| `image.hookRepository`            | Webhook docker file                                                       | `"quay.io/jfardello/hugo-webhook"`    |
| `image.hookRepositoryVersion`     | Image tag for the webhook image                                           | `"latest"`                            |
| `image.pullPolicy`                |                                                                           | `"IfNotPresent"`                      |
| `git.sshPrivateKey`               | The ssh private key in order to git pull/clone when using ssh transport   | `""`                                  |
| `git.existingSshPrivateKeySecret` | When it's set, the sshPrivateKey parameter is ignored                     | `""`                                  |
| `git.provider`                    | When using http transport, the git provider, github, gitlab, or gitea.    | `"GITHUB"`                            |
| `git.transport`                   | Http or ssh                                                               | `"HTTP"`                              |
| `git.webToken`                    | This is the web token when using http transport                           | `"sampletoken"`                       |
| `git.webUsername`                 | Username when using http and a token. (gitea, and gitlab needs this.)     | `"sampleuser"`                        |
| `git.existingWebTokenSecret`      | When it's set, the webToken parameter is ignored                          | `"sampletoken"`                       |
| `git.http_insecure`               | Nasy setting, dont try this unless you're pretty sure of it.              | `"FALSE"`                             |
| `git.repoUrl`                     | This is the repo url, note that there is no schema.                       | `"github.com/jfardello/hugo-webhook"` |
| `git.repoContentPath`             | Hugo will cwd here before build.                                          | `"sample/site"`                       |
| `git.repoBranch`                  | Branch that will be pulled/cloned.                                        | `"master"`                            |
| `git.projectType`                 | hugo or mkdocs.                                                           | `"hugo"`                              |
| `git.manyBranches`                | Do we serve many branches (dev) or only one branch (prod).                | `"FALSE"`                             |
| `git.cloneDest`                   | Destination of the source files.                                          | `"/srv/src"`                          |
| `git.preserveSrc`                 | Preserve src, successive hook calls will pull instead of clone.           | `"TRUE"`                              |
| `ephemeral.mountTo`               | Where to mount the ephemeral hostpath.                                    | `"/srv"`                              |
| `target.baseUrl`                  | Base Url of the target site.                                              | `"/"`                                 |
| `target.baseDir`                  | Destination of the html site (plus baseUrl for mkDocs).                   | `"/srv/static"`                       |
| `target.params`                   | Extra params passed to the hugo build.                                    | `"--minify"`                          |
| `imagePullSecrets`                |                                                                           | `[]`                                  |
| `nameOverride`                    |                                                                           | `""`                                  |
| `fullnameOverride`                |                                                                           | `""`                                  |
| `serviceAccount.create`           |                                                                           | `true`                                |
| `serviceAccount.annotations`      |                                                                           | `{}`                                  |
| `serviceAccount.name`             |                                                                           | `null`                                |
| `podSecurityContext`              |                                                                           | `{}`                                  |
| `securityContext`                 |                                                                           | `{}`                                  |
| `service.type`                    |                                                                           | `"ClusterIP"`                         |
| `service.port`                    |                                                                           | `80`                                  |
| `service.hookPort`                |                                                                           | `9000`                                |
| `ingress.enabled`                 |                                                                           | `false`                               |
| `ingress.traefikTls`              | For properly render Notes.txt, as traefik ingress doesn't use tls section | false                                 |
| `ingress.annotations`             |                                                                           | `{}`                                  |
| `ingress.hosts`                   |                                                                           | `[{"host": "chart-example.local"}]`   |
| `ingress.tls`                     |                                                                           | `[]`                                  |
| `resources`                       |                                                                           | `{}`                                  |
| `nodeSelector`                    |                                                                           | `{}`                                  |
| `tolerations`                     |                                                                           | `[]`                                  |
| `affinity`                        |                                                                           | `{}`                                  |



