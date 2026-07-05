# Vercel Runtime Fix

This package fixes the deployment error:

> Function Runtimes must have a valid version, for example `now-php@1.0.0`.

Cause: `vercel.json` contained an invalid runtime value: `"runtime": "python3.12"`.

Fix: the runtime field has been removed. Vercel auto-detects Python serverless functions from `api/*.py`, while `.python-version` keeps the Python version set to `3.12`.

Use this package instead of the previous full-feature package. Upload the extracted contents to the GitHub repo root, including the hidden `.python-version` file.
