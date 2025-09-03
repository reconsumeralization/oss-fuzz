# Internal Security Issue Resolution Guide (Private)

Version: 1.0 • Last updated: {{auto}}
Audience: Security researchers, maintainers, and patch authors
Confidentiality: Private. Do not share externally. No public posting prior to coordinated disclosure.

---

## Mission and Principles

- Validation First: Every finding is reproduced with a deterministic, minimal PoC before reporting.
- Responsible Disclosure: Follow VRP/CVD processes, respect embargoes, keep details private.
- Patch-Ready: Every report includes a production-quality fix, tests, and backport guidance.
- Professional Documentation: Clear impact, repro steps, artifacts (logs/screens), and mitigation.
- Defense-in-Depth: Fix root cause and add systemic safeguards (tests, policies, CI gates).

---

## End-to-End Workflow

0) Intake and triage → 1) Reproduce and validate → 2) Analyze impact and exploitability → 3) Prepare patch and tests → 4) Static/Dynamic analysis + fuzzing → 5) CI/CD hardening + supply chain → 6) Private disclosure + comms → 7) Verify fix + close → 8) Postmortem + learnings

---

## Phase 0: Intake and Triage

- Sources: Bug reports, internal audits, fuzzing, CodeQL/Semgrep alerts, CI failures, user reports.
- Scope and asset: Identify repository, service, component, and data sensitivity (user data, tokens, prod access).
- Duplicate check: Search tracker, commit history, known issues. Link duplicates.
- Ownership: Identify tech owner and security owner.
- Tracking: Open a private issue/ticket with minimal details, link PoC plan, set temporary severity.
- Initial severity rubric (preliminary, will be refined after validation):
  - S1/P1: RCE, auth bypass, token exfil in default config, sandbox escape, supply-chain compromise.
  - S2/P2: Privilege escalation, data exfil requiring significant preconditions, sandbox policy gaps.
  - S3/P3: Info leak, CSRF-like CLI misuse, low-impact DoS.
  - S4/P4: Low signal, hard to exploit, needs unrealistic preconditions.

Checklist (Intake/Triage)
- [ ] Confirm in-scope asset and owner
- [ ] Check for duplicates
- [ ] Create private tracking item
- [ ] Assign preliminary S/P
- [ ] Confirm safe environment for testing

---

## Phase 1: Reproduction and Validation (Validation First)

Environment Hygiene
- Use isolated environments: container (user namespace), VM, or sandbox (gVisor/Firecracker). No prod data.
- Capture artifacts: terminal logs, HTTP traces, screenshots, minimized repo snapshot, PoC script.
- Instrumentation: Enable verbose logs, network capture (tcpdump/mitmproxy as needed), disable analytics/telemetry.

PoC Standards
- Deterministic: Same inputs → same outcome. Seed random sources.
- Minimal: Remove non-essential steps/dependencies. Keep PoC under ~200 LOC where feasible.
- Safe-by-default: No data exfil to third parties; loopback only. Include a clear kill-switch and cleanup.
- Reproducible: Document env (OS, versions, commit SHA), commands, expected outputs, and timing.
- Evidence: Include exact logs, stack traces, and artifacts proving the vulnerability.

PoC Harness Patterns
- TypeScript/Node: Use `tsx` or `node --conditions=production` with strict ESLint; avoid global installs.
- Python: Use venv, `python -I`, `pip install --no-cache-dir -r requirements.txt` with hashes.
- Go: Use modules, pinned versions, `go test -run TestExploit -v` style harness, context timeouts.
- Rust: `cargo run --locked`, `cargo fuzz` for fuzzable surfaces, deny `unsafe` by default.
- Bash: `set -euo pipefail`, quote variables, `mktemp -d` for scratch space, traps for cleanup.

Checklist (Validation)
- [ ] Isolated environment prepared
- [ ] Minimal, deterministic PoC created
- [ ] Reproducible instructions documented
- [ ] Evidence artifacts captured and stored privately

---

## Phase 2: Impact and Exploitability Analysis

- Threat modeling (STRIDE): Identify spoofing, tampering, repudiation, information disclosure, DoS, elevation.
- Preconditions: Auth level, network position, local/remote, required capabilities.
- Blast radius: Single-user, multi-tenant, infra-wide, supply-chain propagation.
- Realistic attack chain: Link to other weaknesses (token handling, sandbox, MCP tools, CI secrets).
- Impact quantification: Data at risk, execution capability, persistence, lateral movement potential.
- Severity mapping: Convert analysis to S1–S4 and VRP P0–P3. Note user harm and fix complexity.

Checklist (Impact)
- [ ] Preconditions realistically defined
- [ ] Attack chain diagram or narrative
- [ ] Severity mapped with rationale

---

## Phase 3: Patch Strategy and Development (Patch-Ready)

General Fix Patterns
- Validate inputs early; prefer allowlists over denylists.
- Enforce authentication and least-privilege authorization at boundaries.
- Default secure configurations; opt-out only with explicit, warned toggles.
- Normalize and canonicalize paths/inputs before use. Avoid dangerous APIs.
- Remove gadget chains; disable dynamic eval and template injection sinks.
- Add invariant checks and rate limits for risky operations.

Language-Specific Guidance

TypeScript/Node
- Enable TypeScript strict mode; runtime validation with `zod`/`valibot` for untrusted inputs.
- Avoid `child_process.exec`; prefer `spawnFile` with argument arrays; never interpolate untrusted strings.
- Quote and escape shell args; use `cross-spawn`, `execa` with `stdio: pipe`, timeouts.
- Prevent prototype pollution: deep clone, `Object.create(null)` for dicts, validate JSON schema.
- Filesystem: use `path.join` + `path.normalize`, validate against a jailed root.
- Package boundaries: define `exports` and `types` in `package.json`; avoid implicit fallbacks.
- Secrets: never log tokens; use redaction middleware.

Python
- Use `subprocess.run([...], check=True)`; avoid `shell=True`. Use `shlex.quote` if needed.
- Deserialize safely: `yaml.safe_load`, `json.loads` with schema validation.
- Filesystem: `os.path.realpath` + `os.path.commonpath` to enforce jail; avoid temp races -> `mkstemp`.
- Networking: set timeouts, retries with backoff; verify TLS; pin hosts when appropriate.
- Virtualenvs: per-project venv; `pip-tools` with hashes.

Go
- Context everywhere (timeouts/cancellation). Avoid blocking goroutines without backpressure.
- HTTP: use `http.Server` timeouts; template escaping (`html/template`).
- Filesystem: validate with `path/filepath.Clean` and prefix checks; restrict symlinks.
- Crypto: use `crypto/subtle` for comparisons; standard libs only.
- Build: `-trimpath`, Repro builds, disable CGO unless necessary.

Rust
- Deny `unsafe` unless justified and reviewed. Add Miri/Clippy to CI.
- Serialization: `serde` with `deny_unknown_fields`, strict enums.
- Concurrency: prefer `Arc<Mutex<...>>` only when needed; avoid deadlocks with clear ownership.
- Command exec: use structured args; validate inputs.

Bash
- `set -euo pipefail` and `IFS=$'\n\t'`. Quote everything. Use arrays for args.
- Use `mktemp` for files/dirs; trap cleanup; avoid parsing `ls`; prefer `find -print0` + `xargs -0`.

Testing and Regression
- Add unit tests that pin the vulnerability; add integration tests reproducing the exploit path.
- Negative tests: incorrect inputs do not cause unsafe behavior.
- Backports: identify supported branches; prepare minimal, safe backports.

Checklist (Patch)
- [ ] Root cause fixed with safe defaults
- [ ] Repro and regression tests added
- [ ] No new security regressions introduced
- [ ] Backport plan prepared

---

## Phase 4: Static/Dynamic Analysis and Fuzzing

Static Analysis
- Semgrep: curate rules for command injection, path traversal, deserialization, token handling, prompt injection sinks.
  Examples
  - TS/Node: detect `child_process.exec`, string concatenation in commands, eval-like APIs.
  - Python: `subprocess.*` with `shell=True`, `yaml.load`, unsafe `pickle`.
  - Go: unsafe path joins, `exec.Command` with concatenated strings.
  - Rust: `Command::new` with user input, `serde` without deny unknown.
- CodeQL: enable query suites for security-and-quality; add custom queries for our code patterns.

Dynamic Analysis (DAST)
- For web surfaces: ZAP/Burp in non-prod env; record and sanitize payloads.
- For CLI: expect-based harness to drive interactive flows; capture stdout/stderr/exit codes.
- For MCP/LLM: red-team prompts in a sandboxed profile, capture model and tool outputs.

Fuzzing
- Go: `go test -fuzz=FuzzTarget -fuzztime=60s` with corpus under `testdata/fuzz`.
- Rust: `cargo fuzz run target` with minimized corpus; integrate with CI.
- Python: `atheris` with corpus and timeout guards.
- OSS-Fuzz: prepare build scripts, seed corpora, minimize, and define sanitizers (ASAN/UBSAN if applicable).

Checklist (Analysis)
- [ ] Static rules executed and triaged
- [ ] Dynamic harness executed safely
- [ ] Fuzzers run with time/corpus limits

---

## Phase 5: CI/CD Hardening and Supply Chain Controls

GitHub Actions
- Pin actions by commit SHA; avoid `@v*`. Use reusable workflows.
- Restrict `GITHUB_TOKEN` permissions (default: `contents:read`); elevate per-job only.
- Use OIDC with short-lived cloud creds and least-privilege roles.
- Block untrusted forks from accessing secrets; require approval for external contributions.
- Artifact integrity: provenance with SLSA generator; sign releases with Sigstore/cosign.

Dependency and Build Security
- Enforce lockfiles (`package-lock.json`, `poetry.lock`, `go.sum`, `Cargo.lock`).
- Configure Renovate/Dependabot with security updates autopilot + review gates.
- SBOM generation (Syft/CycloneDX) and continuous scanning (Grype/Trivy).
- Verify provenance for third-party tools; ban curl|bash installers without checksum/signature.

Pre-commit and Policy
- Pre-commit hooks: secrets scanning, format, lint, Semgrep baseline.
- Protected branches with required checks and code owners.

Checklist (CI/CD & Supply Chain)
- [ ] Actions pinned by SHA; minimal perms
- [ ] Lockfiles enforced; updates monitored
- [ ] SBOM + signing/provenance enabled
- [ ] Pre-commit and policy gates active

---

## Phase 6: Disclosure, VRP Comms, and Timelines

- Prepare private advisory: Executive Summary → Affected Versions → Technical Details → PoC (sanitized) → Impact → Patch → Mitigations → Timeline → Credits.
- VRP Severity and Priority: Map S1–S4 to P0–P3 with exploitability and blast radius.
- Timelines: Initial report → triage ack (24–72h) → fix window (per severity) → coordinated release.
- Embargo: Keep details private; share only with need-to-know until patch is available.
- Communication cadence: Professional, concise, non-speculative; escalate only for active exploitation.

Templates (snippets)
- Initial report subject: "[Private] Vulnerability report: <component> — <short impact>"
- Follow-up: "Confirming receipt and fix status for <issue id>"
- Closure: "Fixed and verified: <component> — <issue id>"

Checklist (Disclosure)
- [ ] Private advisory drafted with all sections
- [ ] VRP submission prepared with evidence and patch
- [ ] Embargo respected; release plan agreed

---

## AI/LLM Security Guidance

Prompt Injection & Tooling
- Normalize inputs and constrain instructions; clearly separate user vs system prompts.
- Constrain tool use: explicit allowlist of MCP tools with argument schemas and budgets.
- Sandboxing: run tools in least-privileged, network-restricted contexts with per-invocation tokens.
- Output filtering: structured output validation (JSON schema), explicit content allowlists.
- Secrets: never include tokens in prompts or logs; redact model outputs; rotate on suspicion.

Evaluation
- Attack libraries: curated red-team prompts for data exfiltration, function-abuse, jailbreaks (private corpus).
- Metrics: success rate, containment rate, time-to-detection.
- Logging: capture model/tool IO with privacy redaction and retention limits.

---

## Gemini CLI / MCP Specific Guidance

Threat Model
- Inputs: local files, environment variables, MCP tool outputs, network endpoints.
- Trust boundaries: CLI process, MCP server, tool subprocesses, filesystem, network.

Common Weaknesses
- Shell command construction from model or untrusted inputs.
- Overbroad file read/write/glob patterns; path traversal via symlinks.
- Token handling: leaking API keys in logs or model context.
- MCP tool abuse: invoking arbitrary subprocesses or network calls.

Defenses
- Explicit tool allowlist with schemas; deny unknown fields.
- No implicit shell: use argument arrays, disable shell expansion.
- File sandbox: project-root jail; validate canonical paths; deny symlinks by default.
- Secret hygiene: redaction middleware; ephemeral tokens scoped per task.
- Rate limits and budgets: constrain number of tool calls and execution time.

PoC Harness
- Create a minimal MCP server with only a benign tool; attempt prompt injection to escape scope.
- Validate defenses: schema enforcement rejects extra fields; filesystem jail blocks traversal; subprocess spawns denied.
- Capture logs of accepted vs rejected tool invocations; assert containment.

---

## Checklists (Quick Use)

Intake/Triage
- [ ] Owner identified, tracker created, prelim severity set
- [ ] Environment for safe testing prepared

Validation/PoC
- [ ] Deterministic, minimal PoC with artifacts
- [ ] No external exfil; cleanup included

Patch
- [ ] Root cause fixed; tests added
- [ ] Backports and changelog prepared

Analysis
- [ ] Semgrep/CodeQL baselines green
- [ ] Fuzzers run with no new crashes

CI/CD & Supply Chain
- [ ] Actions pinned; perms least-privilege
- [ ] SBOM, signing, provenance enabled

Disclosure
- [ ] Advisory and VRP submission ready
- [ ] Embargo and release plan agreed

---

## Report Template (Internal)

Executive Summary
- A concise, non-technical overview of the issue, impact, and fix.

Technical Details
- Root cause, vulnerable codepaths, affected versions, and constraints.

Proof of Concept
- Minimal steps and code to reproduce; expected vs actual.

Impact
- Data at risk, execution capability, blast radius, exploitability.

Mitigation & Patch
- Fix description, configuration mitigations, and backports.

Verification
- Steps and tests that confirm the fix; artifacts.

Timeline
- Discovery → Report → Acknowledgment → Fix → Verification → Release.

Credits
- Researcher(s) and contributors.

---

## Appendices

A) Severity Mapping (Example)
- S1/P1: RCE, sandbox escape, token exfil with zero-click or default path
- S2/P2: Priv-esc, high-impact data exfil with moderate preconditions
- S3/P3: Info disclosure, limited DoS
- S4/P4: Low exploitability or unrealistic preconditions

B) Risk Acceptance
- Criteria for accepting residual risk with documented rationale and compensating controls.

C) Tooling Cheat-Sheet
- Semgrep: `semgrep --config p/ci --config path/to/custom.yml --error --strict`
- CodeQL: `codeql database create db --language=<lang> && codeql database analyze db <suite>.qls --sarif` 
- Go fuzz: `go test -fuzz=FuzzTarget -run=^$ -fuzztime=60s`
- Rust fuzz: `cargo fuzz run target -- -runs=0 -max_total_time=60`
- Python Atheris: `python -m atheris your_fuzz.py -- -max_len=4096`

D) References (Private)
- Internal red-team prompt corpus, custom Semgrep rules, CodeQL queries, OSS-Fuzz onboarding docs.

---

Operating Note: Keep this guide concise, actionable, and updated. Prefer checklists and templates to long prose. All artifacts must remain private.