# Dependency updates

This template checks GitHub Actions weekly with Dependabot. When adding code,
extend `.github/dependabot.yml` for every supported manifest root: use `cargo`
for Cargo workspaces, `npm` for npm/pnpm, `docker` for Dockerfiles,
`docker-compose` for Compose files, and `gitsubmodule` for Git submodules.
Include standalone crates excluded from a parent workspace and any nested
composite-action directories in the Actions job. Add only jobs with
real manifests, allow all dependencies, and use `chore(deps)` commit messages.

Follow the organization [coverage inventory and manual-update checklist](https://github.com/libid-org/libID/blob/main/DEPENDENCIES.md).
Noir manifests, raw Cargo Git SHA pins, tool versions embedded in scripts or
workflow inputs, and generated artifacts need separate review. Do not assume
that adding a Dependabot configuration covers those dependencies.

Configuration must reach the default branch to activate. Forks additionally
need Dependabot version updates explicitly enabled in repository settings.
Security updates and vulnerability alerts are separate settings. Review update
PRs and run CI; this template does not enable auto-merge.

DCO still requires sign-offs, including Dependabot's standard support-address
trailer for its exact bot author identity. Test this with:

```sh
python3 .github/tests/test_dco.py
```
