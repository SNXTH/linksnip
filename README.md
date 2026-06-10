# ⚡ LinkSnip — Your first Python web app

A URL shortener built with Flask + SQLite.

## Setup (do this once)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run it

```bash
python app.py
```

Then open your browser and go to: **http://localhost:5000**

## What you'll learn from this project

- **Routing** — how URLs map to Python functions (`@app.route`)
- **Forms** — how POST requests send data from browser to server
- **SQLite** — storing and retrieving data without a big database setup
- **Templates** — how Jinja2 renders HTML with Python variables
- **Redirects** — how short links forward to long ones

## Project structure

```
linksnip/
├── app.py              ← All the Python logic
├── requirements.txt    ← Dependencies
├── links.db            ← Created automatically when you run it
├── templates/
│   ├── index.html      ← Main page
│   └── 404.html        ← Not found page
└── static/
    └── css/
        └── style.css   ← All the styling
```

## Try extending it

- Add an expiry date to links
- Show a QR code for each short link
- Add a password to protect a link
- Deploy it to the web with Railway or Render (free)
# linksnip
