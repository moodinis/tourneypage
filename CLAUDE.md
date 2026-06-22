# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A GitHub Pages site that displays a Leaflet.js interactive map of 14U youth baseball tournaments for Fall 2026 (Aug–Dec). The map shows tournaments from multiple organizers (Perfect Game, USSSA, Triple Crown Sports, Gametime Tournaments, Genesis Sports Complex) with org- and month-based filter chips.

The HTML file (`fall2026tourneymap.html`) is **generated** — never edit it directly. Edit `build.py` and regenerate.

`index.html` is a single link pointing to `fall2026tourneypage.html` on the GitHub Pages site.

## Build pipeline

```
python build.py
```

Connects to the MySQL database, queries all tournaments where `start_age <= 14 AND end_age >= 14`, generates `fall2026tourneymap.html`, and prompts to commit + push.

Requirements: `mysql-connector-python`

## Database

Cloud MySQL at `34.45.11.139`, database `tourneydatabase`. Two tables:
- `organizers` — id, name
- `tournaments` — name, organizer_id, city, state, start_date, end_date, start_age, end_age, link, lat, lng

## Adding new tournaments

**Option A — from the Excel spreadsheet** (`D:\GoogleDrive\TourneyDB\14UTourneysFall2026.xlsx`, sheet `Tournaments`):
- Add `CITY_COORDS` entries for any new city/state combos
- Add the org to `TARGET_ORGS` if new
- Run `python import_new_tourneys.py`

**Option B — add coords to existing DB rows** (one-off): edit and run `add_coords.py`.

After inserting rows, run `python build.py` to regenerate the HTML.

## Adding a new organizer

1. Insert a row into `organizers` in the DB
2. Add the org name → code mapping to `ORG_CODES` in `build.py`
3. Add the code → label/color entry to `ORG_META` in `build.py`
4. Run `python build.py`

## Deployment

The site is hosted on GitHub Pages (`moodinis.github.io/tourneypage`). `build.py` handles `git add`, `git commit`, and `git push` when prompted.
