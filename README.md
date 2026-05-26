# Backlog Dashboard

A self-contained web dashboard for tracking aging case backlog, with a direct-reports submission form.

---

## Files in this repo

| File | Purpose |
|---|---|
| `index.html` | Main dashboard — charts, metrics, drill-down |
| `submit.html` | Direct reports form — log case closures |
| `backlog_data.json` | Data file the dashboard reads (replace daily) |
| `update_data.py` | Script to regenerate `backlog_data.json` from new Excel |
| `README.md` | This file |

---

## How to publish on GitHub Pages (one-time setup)

1. Create a new **public** repository on GitHub (e.g. `backlog-dashboard`)
2. Upload all files from this folder into the repo root
3. Go to **Settings → Pages → Source → Deploy from branch → main / root**
4. Your URL will be: `https://<your-github-username>.github.io/backlog-dashboard/`

Share that URL with your direct reports. They can:
- View the full dashboard at `/index.html`
- Submit case closures at `/submit.html`

---

## Daily data refresh (when you receive the new Excel)

### Option A — via Claude (easiest)
Upload the new Excel to Claude and ask it to regenerate `backlog_data.json`. Then replace the file in your GitHub repo.

### Option B — run locally (Python 3.8+)

```bash
pip install pandas openpyxl
python update_data.py path/to/new_backlog.xlsx
```

Then commit and push the updated `backlog_data.json`:

```bash
git add backlog_data.json
git commit -m "Refresh backlog data $(date +%Y-%m-%d)"
git push
```

The dashboard updates within ~60 seconds after the push.

---

## Connecting the submission form to SharePoint

The submission form on `submit.html` can post directly to a SharePoint list.

### Steps:
1. Create a SharePoint list called `BacklogClosures` with these columns:
   - `Title` (text) — case number
   - `CaseNumber`, `ClosureDate`, `ProductName`, `CaseRecordType` (text)
   - `Outcome`, `Description`, `SubmittedBy`, `SubmitterEmail` (text)

2. Find your SharePoint REST endpoint:
   ```
   https://<org>.sharepoint.com/sites/<site>/_api/web/lists/getbytitle('BacklogClosures')/items
   ```

3. Paste this URL into the **SharePoint upload target** field at the top of the submission form.

> **Note:** For cross-origin (CORS) requests to work, your SharePoint admin may need to allow the GitHub Pages domain. Alternatively, use the **Export CSV** button and import to SharePoint manually.

---

## Reduction target policy

| Age band | Target |
|---|---|
| < 1 month | No action required |
| 1–2 months | 40% reduction goal |
| 3–4 months | 50% reduction goal |
| 4–6 months | Monitor |
| 6+ months | 100% closure target |

---

## Year-end progress tracking

Each `backlog_data.json` represents a daily snapshot. To build a year-end progress chart:
- Keep a folder of dated JSON files (e.g. `snapshots/2026-05-26.json`)
- At year-end, run a summary script across all snapshots

Ask Claude to build the progress chart view when you have several months of snapshots.
