Use Unlazy by default for substantial multi-part autonomous work.

Keep source, tests, deployment evidence, and current state in Git as work proceeds. Preserve `home-service.json`: it is the project-owned Home build/card contract. Do not add a manual Home catalog entry.

For static/browser work, make the build deterministic and make the published output work under `HOME_BASE_PATH=/apps/<repository>/`; prefer relative assets and links. Run project tests inside the build command when dependencies are required.

Keep `scope.published_surface` and `scope.local_runtime` accurate. A green Home deployment certifies only the published browser surface. Never infer that a native, GPU, database, daemon, or other local runtime is validated because the browser artifact deployed.

If the project no longer fits the static/browser adapter, fail closed and use or extend the Home deployment adapter instead of hiding unsupported runtime work inside the static build.

Never add hosted/paid build workflows without an explicit cost review. Project metadata cannot authorize guest access or carry credentials.

Every owned interface must be dark by default, including initial paint and native controls, regardless of OS preference. Preserve readable contrast and original artwork. Keep dark metadata on every published HTML entrypoint; the build rejects its removal.
