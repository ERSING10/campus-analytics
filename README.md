# Campus Analytics

An automated system that tracks and compares the annual publication count of Turkish universities on Scopus. Built to benchmark Kocaeli University's research output against peer institutions.

## How it works

1. **Data collection** (`fetch_and_update.py`) — Runs automatically three times a day via GitHub Actions, querying the Scopus Search API (`AF-ID(...) AND PUBYEAR IS 2026`) for each university's publication count for the current year.
2. **Data storage** (`data/`) — `ham_log.csv` stores every measurement, `gunluk_ozet.csv` stores the latest value per day. University identifiers are listed in `university_ids.csv`.
3. **Analysis** (`analysis.py`) — Calculates 3-month change (based on monthly averages), 10-day and 30-day change, and a momentum score.
4. **Reporting** (`main.py`, `report.py`) — Generates `report.json` (for the web dashboard) and `report.pdf` (downloadable).
5. **Presentation** (`index.html`, `style.css`, `script.js`) — Displays the results on GitHub Pages, including summary cards, a distribution chart, an activity history chart, and a full comparison table.

## Cost

Fully free infrastructure: GitHub Actions for automation, GitHub Pages for hosting.

## Status

Under active development. Since data accumulates from the day the system started running, the 10-day, 30-day, and momentum fields initially show "insufficient data" and will populate as more history builds up.