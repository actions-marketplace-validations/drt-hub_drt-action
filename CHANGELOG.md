# Changelog

All notable changes to this Action are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- CI: bumped pinned `actions/checkout` (v4 → v7) and `actions/setup-python`
  (v5 → v7) majors; added `.github/dependabot.yml` (github-actions ecosystem,
  weekly) so future majors don't go stale silently again.
- Docs: refreshed the `drt-version` example in README to `0.9.0`.

## [1.0.0] - 2026-06-13

### Added
- Initial release of the `drt sync` composite Action.
- Installs `drt-core` (optionally pinned via `drt-version`, with connector
  `extras`) and runs `drt run`.
- Inputs: `select`, `drt-version`, `python-version`, `extras`,
  `working-directory`, `profiles-file`, `profile`, `dry-run`, `threads`, `args`.
- Outputs: `status`, `succeeded`, `failed`, `duration-seconds`, `result-json`,
  parsed from `drt run --output json`, plus a step-summary table.
- Stages a committed `profiles.yml` to `~/.drt/profiles.yml`; secrets are passed
  through `env:` and resolved by drt's `*_env` keys.
- Hermetic self-test workflow against a local DuckDB fixture (no secrets).

[Unreleased]: https://github.com/drt-hub/drt-action/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/drt-hub/drt-action/releases/tag/v1.0.0
