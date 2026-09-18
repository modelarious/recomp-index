# Home service template

Copy this repository into a new private modelarious project. The local Home controller discovers home-service.json on the default branch, builds in a constrained container, tags the exact source commit and publishes the verified static site. No Home repository entry, GitHub Actions job or per-project credential is required.

Version 1 supports static websites, browser workbenches and prebuilt browser game exports. Persistent backends and native Unity/macOS/Windows builds need their own adapter; unsupported manifests fail RED, never silently skip.

Edit src/ and push to your default branch. Set card details and the build command in home-service.json. The repository name supplies the unique URL. Never put secrets in the source or output. Newly discovered projects are owner-only; project metadata cannot grant Derek access.
