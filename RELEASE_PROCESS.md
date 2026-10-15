# Release process

This document describes how to release the `skore-skills` package and the
skills catalog. You need write access to `probabl-ai/skore-skills` and to the PyPI
project.

Releases use semantic versioning:

- Major and minor releases are numbered `X.Y.0`.
- Patch releases are numbered `X.Y.Z`.

Publishing a GitHub Release creates the source tarball that
`skore skills install` downloads from `probabl-ai/skore-skills`. The installer reads
`releases/latest`, then downloads `/repos/probabl-ai/skore-skills/tarball/{tag}` and
copies each skill from the paths in `.catalog.json`. The same release publishes
the `skore-skills` wheel and sdist to PyPI.

## One-time setup

Before the first publish:

1. On PyPI, add a trusted publisher for `skore-skills`. Use a pending publisher
   when the project does not exist yet.
   - Owner: `probabl-ai`
   - Repository: `skore-skills`
   - Workflow: `release.yml`
   - Environment: `release`
2. On GitHub, create an environment named `release`. Add required reviewers
   when PyPI publishing should wait for approval.

The skills tarball is available as soon as the GitHub Release is published.
PyPI publishing waits on the `release` environment when that environment has
required reviewers.

## Cutting a release

1. Run `pixi run check`.
2. Create a [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
   on the commit to ship. GitHub can create the tag and the release together.
   The tag is the release version, for example `0.8.0`.

[`.github/workflows/release.yml`](.github/workflows/release.yml) writes that
tag into the package metadata and the catalog embedded in the distributions,
then publishes them to PyPI. `skore skills install` records the same tag as
the catalog version when it downloads the release archive.

conda-forge is updated from the PyPI release outside this repository.
