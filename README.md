# Container Guard

**Docker / security** · A deterministic Dockerfile and Compose configuration review tool.

## Run locally

Python 3.11+; no third-party packages required. From the standalone repository checkout root:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

`example.json` is the input contract and contains only synthetic or fictional data. `core.run(payload)` returns a JSON-serializable result. Invalid inputs produce an error and a nonzero CLI exit code.

## What it implements

- Handles Dockerfile continuation lines and comments before evaluating policies.
- Flags root user, unpinned bases, missing healthchecks and broad COPY patterns.
- Reviews Compose privileged mode, host networking, Docker socket mounts and secret-looking environment names.
- Returns evidence, severity and remediation hints without executing containers or shell commands.

## Design and limitations

Static heuristic review, not a vulnerability scanner or security certification. It cannot inspect image contents, CVEs, runtime privileges outside the supplied config, build-stage reachability or resolved environment values. Supply Compose as a parsed JSON object; the bundled example.json contains a Compose object; no compose.yaml is bundled in this repository. Real environment values are never required.

## Suggested next step

Add your own data and domain-specific acceptance tests. Read and understand the implementation before presenting it in interviews. No live deployment is implied.

## Optional container execution

`docker build -t container-guard .` then `docker run --rm --read-only --cap-drop=ALL container-guard`. This one-shot CLI container deliberately has no healthcheck. Builds were not executed in this sandbox.

<!-- AH-INDEPTH-DOCS:START -->
## In-depth engineering guide

### Problem and scope

A deterministic Dockerfile and Compose configuration review tool.

This is an independent runnable reference implementation, with synthetic sample input and explicit limits. It is not a deployed service or independently validated business result.

### Architecture and end-to-end flow

```text
Dockerfile/Compose text or object → normalized directives → heuristic policy findings → severity summary
```

| File | Responsibility |
|---|---|
| core.py | Domain validation and project-specific algorithm/state transitions |
| main.py | Bounded JSON CLI input, demo dispatch and JSON output |
| example.json | Exact reproducible sample input |
| tests/test_core.py | Unit and edge-case coverage |

### Design decisions and trade-offs

1. Dockerfile continuations and comments are normalized. The final build stage is inspected for effective USER and HEALTHCHECK so an earlier build-stage user does not falsely harden the final image.

2. Checks include unpinned bases, broad COPY, root runtime, missing health checks, likely secret variables, privileged mode, host networking and Docker-socket mounts. Findings are heuristic, not a complete parser or vulnerability database.

3. Secret-looking ENV/ARG evidence is redacted to directive/key rather than echoing the value. This is a defense-in-depth measure, not a guarantee that all possible secret encodings will be recognized.

### Reproducible setup

Requires Python 3.11+ and no third-party Python packages. Run from the standalone repository checkout root:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

CLI inputs are JSON objects, bounded to 1 MB. Supported domain errors produce a JSON error on stderr and a nonzero exit; inspect the message rather than treating a failed run as a result. The demo does not require a model key, network access or production data.

### Exact example input

```json
{
  "dockerfile": "FROM python:3.13-slim\nWORKDIR /app\nCOPY . /app\nUSER 10001:10001\nHEALTHCHECK CMD python -c \"print(1)\"\nCMD [\"python\",\"main.py\",\"demo\"]",
  "compose": {
    "services": {
      "app": {
        "read_only": true,
        "cap_drop": [
          "ALL"
        ]
      }
    }
  }
}
```

### Core implementation interfaces

| Callable | Boundary |
|---|---|
| `run(p)` | Implementation boundary; see source for validation and return structure. |

The Python `run` result is JSON-serializable. Inspect the source and `main.py run example.json` output for the exact return keys; do not assume another project’s result schema.

### Test coverage and reproducibility

- `tests/test_core.py::test_root`
- `tests/test_core.py::test_nonroot`
- `tests/test_core.py::test_socket`
- `tests/test_core.py::test_no_execution`
- `tests/test_core.py::test_missing_from`
- `tests/test_core.py::test_final_stage_root`
- `tests/test_core.py::test_secret_redaction`

7 named tests are present in this repository. Run the standalone unittest command above; it includes local HTTP tests where present. The GitHub Actions workflow supports pull requests and manual dispatch; remote CI has not been run as part of this preparation. Docker build/run was not executed; no real cloud/model/production-cluster validation is claimed.

### Security and failure boundaries

Static heuristic review, not a vulnerability scanner or security certification. It cannot inspect image contents, CVEs, runtime privileges outside the supplied config, build-stage reachability or resolved environment values. Supply Compose as a parsed JSON object; the bundled example.json contains a Compose object; no compose.yaml is bundled in this repository. Real environment values are never required.

Never commit .env, real API keys, runtime databases, approval material or customer data. See SECURITY.md. A successful example demonstrates the included workflow, not safe internet deployment.

### Troubleshooting

- **Import error:** run from this project’s own folder; each project intentionally has its own core.py.
- **Invalid sample/schema:** start from example.json, then change one field at a time and read the returned validation message.
- **Port already in use:** stop the previous process or select another --port where server.py exists.
- **SQLite lock/state surprise:** close duplicate processes, confirm PROJECT_DB and back up before deliberate resets. Do not delete unrelated project data.
- **External dependency unavailable:** default demos run offline; live provider calls and container pulls require your own working access and may incur external costs.

### Known limitations

Static heuristic review, not a vulnerability scanner or security certification. It cannot inspect image contents, CVEs, runtime privileges outside the supplied config, build-stage reachability or resolved environment values. Supply Compose as a parsed JSON object; the bundled example.json contains a Compose object; no compose.yaml is bundled in this repository. Real environment values are never required.

### Extension roadmap — not implemented

Use a real Dockerfile/YAML parser, policy versioning, OCI image metadata and a maintained vulnerability scanner; test false positives against representative repositories.
<!-- AH-INDEPTH-DOCS:END -->


## Provenance and standalone layout

Extracted from `applied-ai-engineering-lab/projects/08-container-guard`. The algorithms, CLI, tests, examples and any server/UI/worker/Docker files are retained byte-for-byte. Only documentation, repository hygiene and CI configuration were adapted for standalone use. This checkout needs neither the parent collection catalog nor its runner/publisher. It is a reference implementation, not evidence of a historical production deployment or measured business outcome.
