# Release procedure

Releases require maintainer approval. Follow this order; do not publish from a PR or change `VERSION` by hand.
The workflow remains manual: a `release: published` trigger would conflict with publishing and testing **before**
creating the GitHub release, and could upload the same version twice.

## Approved GitHub Actions release

1. Merge a changelog PR moving the release's `Unreleased` entries under its new version heading.
2. Run **Bump Release Version with PR** with `<X.Y.Z>`. Review the bot PR: its diff must contain only `VERSION`
   and `docs/template/versions.js`. The bot uses `GITHUB_TOKEN`, so its PR does not trigger CI; check the diff
   before merging it. Never hand-edit `VERSION` as a shortcut.
3. Run **Official Release** from the approved `main` commit. Set `to-prod` to `yes` and, preferably,
   `expected-version` to `<X.Y.Z>`. Leave `trusted-publishing` **false** until the external setup below is
   confirmed by the maintainer. The default token route still uses the existing `PYPI_API_TOKEN` secret.
   The workflow checks the version, builds one wheel and one sdist, checks their metadata and runs
   `twine check --strict`. Publishers only download those artifacts: they do not check out or execute repository
   code. API docs deploy only after successful production publication, using the guarded version.
4. Verify the version in [PyPI's package JSON](https://pypi.org/pypi/idnumbers/json).
5. Run **PyPI install test with uv** with `version=<X.Y.Z>`. Wait for **all** Python matrix jobs to succeed.
6. Create the GitHub release on that released commit: tag `v<X.Y.Z>`, title `Release <X.Y.Z>`, notes from the
   changelog. Tick **Create a discussion for this release** and select **Announcements**.

`expected-version` is optional for backwards compatibility, but recommended to catch dispatch mistakes. A dispatch
from a tag must use exactly `v<VERSION>`; normal manual publication from `main` does not require a pre-existing tag.
Only the exact lowercase `to-prod=yes` selects production; all other values (including `YES`, `Yes`, or
surrounding whitespace) select TestPyPI, using `TEST_PYPI_API_TOKEN` and no docs deployment.
Selecting trusted publishing with TestPyPI fails before building; TestPyPI trusted publishing is not prepared here.
There is no automatic token fallback on OIDC failure, and no `skip-existing` bypass.

## STOP: external Trusted Publisher setup required

This is **preparation only**, part of [#327](https://github.com/identique/idnumbers/issues/327).
No release may depend on OIDC until a maintainer has completed and confirmed these human steps:

- On pypi.org, open the `idnumbers` project's **Manage → Publishing** and add a GitHub Trusted Publisher with:
  owner **identique**, repository **idnumbers**, workflow filename **release_to_pypi.yml**, environment **pypi**.
- In GitHub, configure the **pypi** environment with required maintainer approval and deployment branch/tag rules
  restricted to approved release sources (normally `main`). Merely naming the environment in YAML is not protection;
  configure it **before** enabling the input. The build job has read-only permissions and no secrets; only the
  production OIDC publishing job has `id-token: write`. Docs permissions are confined to its separate caller job.
- **Retain `PYPI_API_TOKEN`** and the working default token path. Do not remove secrets or enable trusted publishing
  as part of this preparation PR. TestPyPI retains its separate token.
- With maintainer approval after setup, run the next production release with `trusted-publishing=true`.
  Its dedicated publishing job uses no username/password and enables attestations. It is a top-level job rather
  than a reusable publisher workflow, as required by the publishing action's Trusted Publishing support.
- After successful publication, verify PyPI's provenance/attestation information for **each distribution**:
  check its digest and repository/workflow/source identity against the approved release commit and downloaded
  artifact. Record the first verified trusted release before claiming the migration is complete.
  Local builds and dry runs cannot verify PyPI trust configuration or mint publication attestations.

Token publication explicitly disables attestations: the action's PyPI attestations require Trusted Publishing.
See the [official PyPI setup instructions](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) and
[PyPA publishing action documentation](https://github.com/pypa/gh-action-pypi-publish) for setup and verification.
The issue remains open until external configuration and the first verified trusted release are complete.

## Release workflow runtime maintenance

The [#468](https://github.com/identique/idnumbers/issues/468) audit updates bump/docs checkout to v7,
docs setup-python to v7 and create-pull-request to v8.1.1. Their release manifests use Node.js 24:
[checkout v7.0.1][checkout-runtime], [setup-python v7.0.0][python-runtime] and
[create-pull-request v8.1.1][pr-runtime]. The release workflow already uses checkout/setup-python v7,
upload-artifact v7 and download-artifact v8; its build, publication and authentication routes remain unchanged.

All three workflows pin `ubuntu-24.04` rather than following `ubuntu-latest`:
[GitHub's announced Ubuntu 26.04 migration][ubuntu-migration] runs from October 19 to November 19, 2026.
Docs retain Python 3.10 and pydoctor 22.9.1; release builds retain Python 3.12. Checkout's default credential
persistence remains enabled for the docs workflow's authenticated `gh-pages` branch switch and push; see the
[checkout credential behavior][checkout-credentials]. The bump action retains its token, committer, PR inputs
and outputs. Its `GITHUB_TOKEN` PRs still do not trigger CI ([action documentation][pr-token]).

These are local regression checks and a source audit, not proof of a successful updated workflow run.
Verify the bot PR, publication and docs deployment during the next approved release. The default token route
still disables attestations; external Trusted Publisher setup in #327 remains incomplete and requires separate
maintainer approval. An upstream download-artifact v8 `Buffer()` deprecation warning may persist; it is not
suppressed or claimed fixed by these runtime updates ([upstream action][download-runtime]).

[checkout-runtime]: https://github.com/actions/checkout/blob/v7.0.1/action.yml
[python-runtime]: https://github.com/actions/setup-python/blob/v7.0.0/action.yml
[pr-runtime]: https://github.com/peter-evans/create-pull-request/blob/v8.1.1/action.yml
[ubuntu-migration]: https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/
[checkout-credentials]: https://github.com/actions/checkout/blob/v7.0.1/README.md
[pr-token]: https://github.com/peter-evans/create-pull-request/blob/v8.1.1/README.md#token
[download-runtime]: https://github.com/actions/download-artifact/blob/v8.0.2/action.yml

## Emergency local fallback

Only if GitHub Actions cannot run, obtain explicit maintainer approval for the target version and repository first.
The legacy [PowerShell publish script](scripts/publish.ps1) exists for this exceptional path. Review it before use:
its historical behavior includes changing the version, installing tooling, publishing and tagging, and is **not**
the normal version-bump workflow. Do not blindly execute it or push all tags. Agree on an audited procedure that
preserves the changelog, version PR, published-package checks and final GitHub release ordering above.
