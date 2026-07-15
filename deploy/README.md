# Deploying the Codex

Ansible deploy for [codex-of-the-damned.org](https://codex-of-the-damned.org),
built on the shared roles from
[server-setup](https://github.com/lionel-panhaleux/server-setup)
(the `lionel_panhaleux.server_setup` collection).

## What it does

`deploy.yml` (run against a single host) installs the `codex-of-the-damned`
package from PyPI into a [uv](https://docs.astral.sh/uv/)-provisioned venv,
runs it under gunicorn as a systemd service, and fronts it with nginx (the
`nginx_site` role, reverse proxy + automatic Let's Encrypt).

It deploys **one environment per run**, selected with `-e codex_env=…`:

| env    | domain                                  | gunicorn port | default |
| ------ | --------------------------------------- | ------------- | ------- |
| `prod` | codex-of-the-damned.org (+ www alias)   | 8012          | ✓       |
| `beta` | codex-beta.krcg.org                     | 8013          |         |

Both environments run the **same** PyPI package and live on the same host
(`strasbourg` in server-setup's `deploy-targets.yml`); they differ only by
domain and port. `www.codex-of-the-damned.org` is served as an alias of the
apex (same content, one shared cert) rather than a 301 redirect — the role's
native idiom. DNS for every domain must point at the host before the first run
(Let's Encrypt HTTP-01).

Logs land in journald, one tag per environment (app service **and** its nginx
vhost share it):

```bash
journalctl -t codex_prod -f
journalctl -t codex_beta -f
```

## Variables

Override at the play/CLI level as needed:

| variable            | default      | meaning                                   |
| ------------------- | ------------ | ----------------------------------------- |
| `codex_env`         | `prod`       | environment to deploy (`prod` \| `beta`)  |
| `codex_workers`     | `2`          | gunicorn worker processes                 |
| `codex_user`        | `codex`      | service user                              |
| `codex_home`        | `/opt/codex` | install tree (one venv per env inside)    |
| `codex_environments`| see playbook | per-env domain, aliases, port             |

## Running from CI

The [deploy workflow](../.github/workflows/deploy.yml) is **manual**
(`workflow_dispatch`) — the Codex is released by hand (`make release`), so run
this from the Actions tab once the new version is on PyPI, choosing `prod` or
`beta`. It targets the `production` GitHub environment and reads, from it:

- `DEPLOY_HOST` (variable) — the target server IP;
- `DEPLOY_HOST_KEY` (variable) — the server's SSH host key line;
- `DEPLOY_SSH_KEY` (secret) — the private deploy key.

These are pushed to the repo by server-setup's `just sync` / `just sync-key`
recipes (the Codex maps to the `strasbourg` host in server-setup's
`deploy-targets.yml`). Both environments share them since they're one host.

## Running locally

```bash
ansible-galaxy collection install -r requirements.yml
ansible-playbook deploy.yml -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy            # prod
ansible-playbook deploy.yml -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy -e codex_env=beta
```

(Run from this `deploy/` directory so `ansible.cfg` is picked up. Add
`--check --diff` for a dry run.)

## First-time cutover from the old myserver deploy

The legacy Flask/uWSGI vhosts claim the same `:443` server names, so nginx
won't serve the new site until they're removed. Run
[`cleanup.yml`](cleanup.yml) **once**, immediately before the first
`deploy.yml`, for each environment:

```bash
ansible-playbook cleanup.yml -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy
ansible-playbook deploy.yml  -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy                 # prod
ansible-playbook deploy.yml  -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy -e codex_env=beta
```

`cleanup.yml` keeps the existing Let's Encrypt certs — the new deployment
reuses them (and `--expand`s the apex cert to add the www SAN).
