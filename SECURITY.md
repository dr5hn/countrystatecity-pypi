# Python package security

Report suspected compromise or vulnerabilities privately to support@countrystatecity.in. Do not post credentials, tokens or exploit details in public issues. Include the package, version, affected file hashes and a minimal reproduction without secrets.

## Release safeguards

The publishing workflow accepts an explicit package selection and a full commit SHA equal to the workflow's own commit on `main`, so the attested source identity matches the build. It tests and builds packages in read-only jobs without saved Git credentials or PyPI credentials. Release dependencies and transitive dependencies are pinned with SHA-256 hashes; builds disable dependency resolution and isolated backend downloads.

The upload job downloads that run's immutable artifacts on a fresh runner. It does not check out source, install project dependencies or run project build hooks. PyPI authentication uses short-lived OIDC credentials and produces publish attestations. No API-token fallback is supported. Publication requires the `pypi` environment, restricted to `main` and approval by the owner.

Workflow actions are pinned to full commit SHAs. Dependabot proposes reviewed updates with a seven-day cooldown; dependency review and a separate audit check known advisories. Hashes prevent unexpected dependency bytes, not malicious code already accepted into a lockfile. Review dependency ownership, release history, advisories and source changes before updating pins.

## Trusted publisher configuration

Each of these PyPI projects needs its own publisher entry:

- `countrystatecity-countries`
- `countrystatecity-timezones`
- `countrystatecity-currencies`
- `countrystatecity-translations`
- `countrystatecity-phonecodes`
- `countrystatecity-regions`
- `countrystatecity-postal-codes`
- `countrystatecity-api`

Use owner `dr5hn`, repository `countrystatecity-pypi`, workflow `publish.yml`, and environment `pypi`. Keep the upload in this top-level workflow rather than a reusable workflow. After migration, remove the repository's old `PYPI_TOKEN` secret. Revoke its underlying PyPI token only after checking whether other legitimate publishing systems still use it.

Before approving a release, inspect its exact source commit, dependency changes, tests, built wheel/sdist identities, notices and dataset provenance. For a retry after an upload error, inspect PyPI first: never replace or blindly republish an accepted version. Partial publication or failed verification needs investigation, not `skip-existing`.

## Account and repository controls

Keep PyPI and GitHub two-factor authentication enabled, preferably with passkeys or hardware security keys. Review collaborators, trusted publishers, sessions and security history periodically. Keep recovery codes offline and never share them with automation.

Versions and changelogs belong in the release PR. The data updater prepares them before opening its PR; release preparation only validates the merged PR at the current `main` tip and cannot push commits. The expired November auto-merge hook has been retired.

Main branch protection requires PRs and the `Release safety gate`, `review` and `audit-release-dependencies` checks, including for administrators. The stable safety gate includes every package/Python test job. Force pushes and branch deletion are disabled. This single-maintainer repository does not require a second person's approval; `CODEOWNERS` requests owner attention but is not a second-person security guarantee. The protected PyPI deployment still requires owner approval.

Bot-created PRs use the built-in GitHub token and explicitly dispatch read-only CI at the generated branch, because those PRs do not trigger normal PR workflows. No persistent CI token or protected-branch bypass is required. Merge only the exact tested head, and never weaken protection to recover a failed release.

These controls reduce exposure; they do not prove the source, dependencies or maintainer account cannot be compromised. A publish attestation identifies the publishing workflow, not a malware-free package.

## Dependency updates and consumer installs

Keep `.github/requirements/release.txt` as the complete release dependency closure for Python 3.15. Update exact versions and wheel hashes in a focused PR, verify availability on Linux x86_64 and macOS arm64, run the dependency audit, and test all eight builds. Do not regenerate the lockfile automatically during publication. Runtime dependency ranges remain library-compatible; consumers should maintain their own application lockfiles.

Prefer wheels from the official PyPI project, pin application dependencies with hashes, avoid untrusted extra package indexes, and inspect [PyPI provenance](https://docs.pypi.org/using-pypi/package-security/provenance/) for releases published after the OIDC migration.

References: [GitHub Actions security](https://docs.github.com/en/actions/reference/security/secure-use), [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/security-model/), and [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/).
