# Setup

This repository holds the GitHub profile README plus two optional, automatically refreshed assets. `README.md` itself is plain text and does not currently embed either asset.

## Profile stats card

- `light_mode.svg` / `dark_mode.svg` are a terminal-style profile card (light and dark palettes).
- `update_profile.py` fills in the elements with IDs `repo_data`, `star_data`, `follower_data`, `commit_data`, `loc_data`, `loc_add` and `loc_del` using the GitHub REST and GraphQL APIs. All other text in the cards is static and edited by hand.
- `.github/workflows/profile.yml` (**Update profile stats**) runs the script daily at 05:17 UTC, on manual dispatch, and on pushes to `main` that change the workflow or the script, then commits any changes to the two SVGs.

`Lines of Code` is calculated from GitHub contributor statistics for public repositories you own where GitHub exposes contributor stats. It is not guaranteed to include every line you have written in repositories owned by other people or organizations.

To show the card on the profile, add this to `README.md`:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/RohanGottipati/RohanGottipati/main/dark_mode.svg">
  <img alt="Rohan Gottipati's GitHub profile" src="https://raw.githubusercontent.com/RohanGottipati/RohanGottipati/main/light_mode.svg">
</picture>
```

To run the script locally (Python 3.12 is used in CI):

```bash
pip install requests
GITHUB_TOKEN=<token> GITHUB_USERNAME=RohanGottipati python update_profile.py
```

- `GITHUB_TOKEN` (required): token used for GitHub API requests.
- `GITHUB_USERNAME` (optional, defaults to `RohanGottipati`): account to collect stats for.

## Contribution snake

`.github/workflows/snake.yml` (**Generate Contribution Snake**) uses `Platane/snk` to render the contribution graph as a snake animation daily at 00:00 UTC (and on manual dispatch or pushes to `main` that change the workflow or `README.md`), and publishes `github-contribution-grid-snake.svg` and `github-contribution-grid-snake-dark.svg` to the `output` branch.
