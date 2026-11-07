# Security notes

This is a local educational reference implementation, not an audited production service. All bundled examples use synthetic or fictional data. No credentials or external service accounts are required.

- Never commit real API keys, .env files, private keys, runtime databases, logs, customer datasets or personal booking information. Review ignored files and every outgoing commit before publishing.
- Where a local HTTP server is included, it binds to 127.0.0.1 by default and has no accounts or authentication. Do not expose it publicly as-is. Host/Origin checks, JSON mutation headers, body limits and safe text rendering are defenses in depth, not substitutes for authorization, TLS or a production server.
- SQLite data values use placeholders. Runtime state belongs in ignored local storage; back up before any deliberate reset.
- The queue executes only allowlisted short sum/word-count jobs, with at-least-once semantics and a 30-second lease. Add durable side-effect idempotency and lease renewal before external work.
- Container Guard is a static heuristic policy linter, not a CVE scanner or security certification. Review real image digests and environment configuration independently.
- Docker image/Compose execution and public production deployment have not been validated in this preparation. Local tests are not a security audit.

Before public deployment, add authentication/authorization, request throttling, HTTPS, managed secrets, migrations, audit retention, monitoring and an independent security review. Do not post sensitive data or exploit credentials in public issues; use a private reporting channel agreed with the maintainer.
