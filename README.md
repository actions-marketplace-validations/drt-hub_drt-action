# drt sync — GitHub Action

Run [**drt**](https://github.com/drt-hub/drt) reverse-ETL syncs in your CI/CD pipelines. This Action installs `drt-core`, runs `drt run`, and exposes the result (status, rows, duration) as step outputs — so you can sync after dbt finishes, on a schedule, or on every push.

```yaml
- uses: drt-hub/drt-action@v1
  with:
    select: '*'
    extras: postgres
  env:
    PG_PASSWORD: ${{ secrets.PG_PASSWORD }}
```

## Quick start

1. Commit a drt project to your repo (a `drt_project.yml`, a `syncs/` directory, and a `profiles.yml`). The `profiles.yml` should reference secrets by **environment-variable name** (e.g. `password_env: PG_PASSWORD`) — never inline secret values.
2. Add a workflow:

```yaml
name: drt sync
on:
  schedule:
    - cron: '0 * * * *'   # hourly
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: drt-hub/drt-action@v1
        with:
          select: '*'
          extras: postgres        # install the connector extras you need
        env:
          PG_PASSWORD: ${{ secrets.PG_PASSWORD }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

## How secrets work

drt resolves credentials from environment variables named by the `*_env` keys in your `profiles.yml`. Because only the env-var **names** live in the file, `profiles.yml` is safe to commit. Supply the real values through the step's `env:` block, sourced from [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets):

```yaml
# profiles.yml (committed)            # workflow step
prod:                                 #   env:
  type: postgres                      #     PG_PASSWORD: ${{ secrets.PG_PASSWORD }}
  host: db.example.com
  user: etl
  password_env: PG_PASSWORD           # ← drt reads $PG_PASSWORD at runtime
```

The Action stages your `profiles.yml` (see the `profiles-file` input) to `~/.drt/profiles.yml`, which is where drt looks for it.

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `select` | `*` | Sync selector: a sync name, a tag (`tag:crm`), or `*` / `all` for every sync. |
| `drt-version` | _(latest)_ | Version of `drt-core` to install (e.g. `0.9.0`). Empty installs the latest release. |
| `python-version` | `3.12` | Python version to set up (drt-core requires >= 3.10). |
| `extras` | _(none)_ | Comma-separated `drt-core` extras for your connectors (e.g. `postgres,bigquery`). |
| `working-directory` | `.` | Directory containing `drt_project.yml` and `syncs/`. |
| `profiles-file` | `profiles.yml` | Path (relative to `working-directory`) to your `profiles.yml`; staged to `~/.drt/profiles.yml`. Set empty to skip. |
| `profile` | _(project default)_ | Profile name to use (overrides `DRT_PROFILE` and the `drt_project.yml` profile key). |
| `dry-run` | `false` | Preview without writing data. |
| `threads` | `1` | Number of parallel sync threads. |
| `args` | _(none)_ | Extra raw arguments appended to `drt run` (escape hatch). |

## Outputs

| Output | Description |
| --- | --- |
| `status` | Overall result: `success` or `failed`. |
| `succeeded` | Number of syncs that succeeded. |
| `failed` | Number of syncs that failed. |
| `duration-seconds` | Total wall-clock duration of all syncs, in seconds. |
| `result-json` | Full JSON document from `drt run --output json`. |

The job fails (non-zero exit) if any sync fails, so a red check is enough for most pipelines. The outputs are there when you want to branch, notify, or record metrics:

```yaml
      - uses: drt-hub/drt-action@v1
        id: sync
        with: { select: 'orders_to_pg', extras: postgres }
        env: { PG_PASSWORD: ${{ secrets.PG_PASSWORD }} }
      - if: always()
        run: echo "drt: ${{ steps.sync.outputs.status }} — ${{ steps.sync.outputs.succeeded }} ok, ${{ steps.sync.outputs.failed }} failed"
```

## Examples

### Run after dbt

```yaml
jobs:
  transform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: dbt build           # build your models first
  reverse-etl:
    needs: transform             # then push them to your tools
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: drt-hub/drt-action@v1
        with:
          select: 'tag:crm'
          extras: bigquery
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_KEY_PATH }}
          HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
```

### Preview on pull requests

```yaml
on: pull_request
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: drt-hub/drt-action@v1
        with:
          select: '*'
          dry-run: 'true'
          extras: postgres
        env:
          PG_PASSWORD: ${{ secrets.PG_PASSWORD }}
```

A runnable, no-secrets example lives in [`examples/workflow.yml`](examples/workflow.yml) and the hermetic project the Action tests itself against is in [`test/fixtures/duckdb_project/`](test/fixtures/duckdb_project/).

## Versioning

Pin to the major tag to get non-breaking updates automatically:

```yaml
- uses: drt-hub/drt-action@v1        # recommended
- uses: drt-hub/drt-action@v1.0.0    # exact pin
```

## License

[Apache-2.0](LICENSE) — same as [drt](https://github.com/drt-hub/drt). ⭐ the [drt repo](https://github.com/drt-hub/drt) if this is useful.
