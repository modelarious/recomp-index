# Home service template

Choose **Use this template → Create a new repository**, keep the owner `modelarious`, then edit and push your project. No Home website entry, webhook, per-project secret, GitHub Actions workflow or manual deployment registration is needed.

The `home-service.json` file opts the project into the installed private Home pipeline. Its card name, description and category become the Home card; `${repo}` uses the repository name. `.home/build.py` builds the starter `src/` into `dist/`.

A controller on the Mac discovers default-branch changes. Punchcard builds them in a non-root, resource-limited container. Successful output is archived on the NAS, an annotated `home-<commit>` Git tag records the source/package checksums, and an atomic switch publishes the site at `/apps/<repository-name>/`. Home discovers the resulting card automatically. Failed builds leave the last working version intact.

Status and urgent warnings are at `http://home.lan/status.html`. Source polling is about 60 seconds; independent audits about 120 seconds. A failed build is red; a pending update turns red after 15 minutes. The existing notification channel receives urgent failure/recovery messages, subject to actual device subscription and delivery.

## Supported in v1

Static websites, browser workbenches, and already-exported browser games. Linux Python 3.12 and Node 24 runners are installed. Persistent backends, database migration, native Unity/editor builds, Windows/macOS executables, submodules and Git LFS assembly require additional adapters. Unsupported manifests fail visibly. The template has no monthly hosted-build or hosted-artifact quota because those services are not used.

Each build gets 2 CPUs, 4 GiB RAM and 256 processes; at most two builds run concurrently. Output is bounded to 512 MiB / 30,000 files, source archives to 256 MiB, index.html to 8 MiB and build duration to 40 minutes maximum. Runner images are pinned locally. All successful packages are retained until an explicitly reviewed policy changes that; low storage stops work rather than purchasing more.

`HOME_BASE_PATH=/apps/<repository-name>/` is available to the build. Configure the framework to consume it or use relative assets/hash routing. Builds have no network by default. Dependency installation requires `build.network: true`; run tests in the build command before producing the output directory. The pipeline does not silently rewrite application bundles or prove every app feature works.

Only trusted owned code should use this template. Build containers receive no GitHub credentials or Docker socket, but this is not an untrusted-code hosting service. New projects are owner-only; metadata cannot grant Derek access. The Mac, Punchcard and storage must be available, and the Mac services require the user session. Total home power/internet failure has no off-site alarm in this release.

Use Unlazy by default for substantial work; commit source, tests, evidence and requirements as work proceeds. Preserve the opt-in contract. Do not add paid/hosted build workflows without an explicit cost review.

Implementation and operations are in `modelarious/modelarious.github.io`, branch `private-home`, directory `pipeline/`. The existing older apps are not all migrated merely by creating this template.
