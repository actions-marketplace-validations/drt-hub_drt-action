"""Parse `drt run --output json` and emit GitHub Action outputs + a step summary.

Usage: emit_outputs.py <result.json> <drt-exit-code>

Reads the JSON document drt writes to stdout (captured to a file by action.yml),
then writes the action's outputs to $GITHUB_OUTPUT and a human-readable table to
$GITHUB_STEP_SUMMARY. Never raises on a malformed document — it degrades to a
"failed" status and a warning annotation so the job still surfaces the problem.
"""

from __future__ import annotations

import json
import os
import sys
import uuid


def _set_output(name: str, value: object) -> None:
    """Append name=value to $GITHUB_OUTPUT, using heredoc form for multiline."""
    target = os.environ.get("GITHUB_OUTPUT")
    text = str(value)
    if not target:
        print(f"[output] {name}={text}")
        return
    with open(target, "a", encoding="utf-8") as fh:
        if "\n" in text:
            delim = f"ghadelim_{uuid.uuid4().hex}"
            fh.write(f"{name}<<{delim}\n{text}\n{delim}\n")
        else:
            fh.write(f"{name}={text}\n")


def _write_summary(data: dict, status: str) -> None:
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return
    succeeded = data.get("succeeded", 0)
    failed = data.get("failed", 0)
    duration = data.get("total_duration_seconds", 0)
    icon = "✅" if status == "success" else "❌"
    lines = [
        "### drt sync result",
        "",
        f"{icon} **{status}** — {succeeded} succeeded, {failed} failed, {duration}s total",
        "",
        "| Sync | Status | Rows synced | Duration (s) | Error |",
        "| --- | --- | --- | --- | --- |",
    ]
    for sync in data.get("syncs", []):
        err = sync.get("error") or ""
        first_line = err.splitlines()[0] if err else ""
        lines.append(
            f"| {sync.get('name', '')} | {sync.get('status', '')} "
            f"| {sync.get('rows_synced', '')} | {sync.get('duration_seconds', '')} "
            f"| {first_line} |"
        )
    with open(target, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    result_path = sys.argv[1] if len(sys.argv) > 1 else ""
    exit_code = sys.argv[2] if len(sys.argv) > 2 else "1"

    data: dict = {}
    try:
        with open(result_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"::warning::could not parse drt JSON output ({exc}); marking run as failed")

    succeeded = data.get("succeeded", 0)
    failed = data.get("failed", 0)
    duration = data.get("total_duration_seconds", 0)
    status = "success" if (exit_code == "0" and failed == 0) else "failed"

    _set_output("status", status)
    _set_output("succeeded", succeeded)
    _set_output("failed", failed)
    _set_output("duration-seconds", duration)
    _set_output("result-json", json.dumps(data, separators=(",", ":")))
    _write_summary(data, status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
