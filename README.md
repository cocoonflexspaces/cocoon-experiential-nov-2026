# The Experiential × Cocoon — Holiday activation proposal (Nov 2026)

Client-facing landing page comparing **Casa Joy** and **Casa Mas** for a two-day holiday brand
activation (Nov 20 creator preview + Nov 21 public day), Options A and B.

- `index.html` — the page (generated, do not edit by hand)
- `pricing.py` — every number on the page. **Drop OTI's removal/reset quote into `OTI_REMOVAL_RESET`** and rebuild.
- `template.html`, `css_base.css`, `css_extra.css` — page source (Cocoon brand system, same as the Fendi deck)
- `build.py` — renders `index.html` and rebuilds the ZIP bundles in `downloads/`
- `img/`, `docs/`, `downloads/` — photos, Casa Mas floor plans, download bundles

```bash
python3 build.py      # after editing pricing.py or template.html
bash deploy.sh        # push to GitHub Pages (needs gh CLI logged in)
```

Brand name of the end client is intentionally kept off the page, title and URL (NDA). The page is `noindex`.
