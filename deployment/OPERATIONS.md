# Home publishing operations

This repository publishes itself. Do not add a card to the Home repository.

## Normal release

1. Update the project and its tests.
2. Keep `home-service.json` accurate, especially `scope.published_surface` and `scope.local_runtime`.
3. Run the project's normal tests plus `python3 .home/build.py`.
4. Commit and push the default branch.
5. Wait for `http://home.lan/status.html` to show this repository green.

Green means the GitHub default-branch commit, annotated `home-<commit>` receipt, retained NAS package, and served bytes agree. It certifies only `scope.published_surface`.

## Failure and rollback

A failed build must leave the last good site online and turn the project red. Fix with a new commit. For rollback, push a new `git revert` commit; do not force-reset the branch to an old already-published SHA.

## Boundaries

The current Home adapter publishes static browser output only. Persistent backends, databases, native executables, Unity editor builds, GPU runtimes, Git LFS, and submodule assembly require a reviewed adapter instead of being hidden inside this contract.

Project metadata never grants guest access. Hosted/paid build automation must not be added without an explicit cost review.
