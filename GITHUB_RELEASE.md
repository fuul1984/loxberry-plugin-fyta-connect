# GitHub publication and automatic releases

## 1. Create the repository

Upload the contents of the GitHub source ZIP to the root of a new GitHub repository. `plugin.cfg` must be in the repository root.

## 2. Configure LoxBerry AutoUpdate

Run locally from the repository root:

```bash
./tools/configure_autoupdate.sh YOUR_GITHUB_USER YOUR_REPOSITORY
```

This creates `release.cfg` and `prerelease.cfg` and enables the corresponding URLs in `plugin.cfg`. Commit and push these changes.

## 3. Publish release 1.0.1

```bash
git add .
git commit -m "Release 1.0.1"
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

The workflow `.github/workflows/release.yml` then builds `FYTA_Connect_v1.0.1.zip` and attaches it to a GitHub Release.

For later releases, update `VERSION` in `plugin.cfg`, `release.cfg` and the changelog before creating the new tag.
