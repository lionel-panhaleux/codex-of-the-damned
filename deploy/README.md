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
| `beta` | codex-beta.krcg.org                     | 8013          | ✓       |
| `prod` | codex-of-the-damned.org (+ www alias)   | 8012          |         |

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
| `codex_env`         | `beta`       | environment to deploy (`beta` \| `prod`)  |
| `codex_workers`     | `2`          | gunicorn worker processes                 |
| `codex_user`        | `codex`      | service user                              |
| `codex_home`        | `/opt/codex` | install tree (one venv per env inside)    |
| `codex_environments`| see playbook | per-env domain, aliases, port             |

## Running from CI

The [deploy workflow](../.github/workflows/deploy.yml) is **manual**
(`workflow_dispatch`) — the Codex is released by hand (`make release`), so run
this from the Actions tab once the new version is on PyPI, choosing `prod` or
`beta`. **Always deploy `beta` first, then `prod`**, for every release, so beta
stays aligned with prod:

```bash
gh workflow run deploy.yml -f environment=beta   # wait for success, check codex-beta.krcg.org
gh workflow run deploy.yml -f environment=prod
```

It targets the `production` GitHub environment and reads, from it:

- `DEPLOY_HOST` (variable) — the target server IP;
- `DEPLOY_HOST_KEY` (variable) — the server's SSH host key line;
- `DEPLOY_SSH_KEY` (secret) — the private deploy key.

These are pushed to the repo by server-setup's `just sync` / `just sync-key`
recipes (the Codex maps to the `strasbourg` host in server-setup's
`deploy-targets.yml`). Both environments share them since they're one host.

## Running locally

```bash
ansible-galaxy collection install -r requirements.yml
ansible-playbook deploy.yml -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy            # beta (first)
ansible-playbook deploy.yml -i "1.2.3.4," --user deploy --private-key ~/.ssh/deploy -e codex_env=prod
```

(Run from this `deploy/` directory so `ansible.cfg` is picked up. Add
`--check --diff` for a dry run.)
