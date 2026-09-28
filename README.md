# Home service template

Use this GitHub template for a new static website, browser workbench, or already-exported browser game that should appear automatically on `home.lan`.

## What happens

1. Create the repository from this template under `modelarious`.
2. Edit the project and `home-service.json`.
3. Push the default branch.
4. Home automatically builds the browser app and, by default, a signed Android WebView package. Remove the `android` declaration only when an Android surface is genuinely inappropriate.
4. The existing Home controller discovers it automatically, Punchcard builds it, and Home adds the card. No Home-repository edit, webhook, per-project secret, or hosted build workflow is required.
5. Verify green at `http://home.lan/status.html`.

A successful build is packaged on the NAS, receives an annotated `home-<commit>` Git tag containing source/artifact evidence, and is published atomically at `/apps/<repository-name>/`. A failed build leaves the last good version online.

## Contract

`home-service.json` owns the card, build command, and deployment scope. `scope.published_surface` says what a green Home deployment actually certifies. `scope.local_runtime` names anything local/native/GPU/backend that remains outside that certification boundary.

The default build uses only Python's standard library, validates relative links, rejects root-relative paths that would break under `/apps/<repository>/`, and assembles the site twice to prove deterministic output. Replace it with the project's real build when needed, but preserve the same fail-closed properties.

## Current adapter limits

Home v1 publishes static directories containing `index.html`. Persistent backends, database migrations, Unity/editor builds, native executables, GPU runtimes, Git LFS, and submodule assembly need separate reviewed adapters. Do not disguise them as static publication.

Builds use existing Mac/Punchcard/NAS resources, not hosted GitHub Actions build minutes or hosted artifacts. The normal pipeline therefore has no monthly cloud-build counter. Existing electricity, storage, network use, dependency services, GitHub API limits, and unrelated repository workflows still apply.

Use Unlazy by default for substantial work. Keep source, tests, evidence, and `CURRENT_STATE.md` in Git. See `deployment/OPERATIONS.md` for release and rollback behavior.
