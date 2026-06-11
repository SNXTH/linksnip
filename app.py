from pathlib import Path
from secrets import choice
from typing import Optional
from urllib.parse import urlparse

import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'links.db'
SHORT_ID_LENGTH = 6
RECENT_LINKS_LIMIT = 5
MAX_ID_ATTEMPTS = 1000

app = Flask(__name__)
DATABASE = str(DB_PATH)


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        database_path = DATABASE
        connection = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


@app.teardown_appcontext
def close_db(error: Optional[BaseException] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    database_path = DATABASE
    with sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        con.execute(
            '''
            CREATE TABLE IF NOT EXISTS links (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                visits INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        con.commit()


def generate_short_id(length: int = SHORT_ID_LENGTH) -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    db = get_db()

    for _ in range(MAX_ID_ATTEMPTS):
        code = ''.join(choice(alphabet) for _ in range(length))
        if not db.execute('SELECT 1 FROM links WHERE id = ?', (code,)).fetchone():
            return code

    raise RuntimeError('Unable to generate a unique short link. Please try again later.')


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError('Please enter a URL.')

    if not value.startswith(('http://', 'https://')):
        value = f'https://{value}'

    parsed = urlparse(value)
    if not parsed.netloc:
        raise ValueError('Please enter a valid URL.')

    return parsed.geturl()


@app.before_request
def ensure_database() -> None:
    init_db()


@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    short_url: Optional[str] = None
    error: Optional[str] = None
    original_url = ''

    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()
        try:
            long_url = normalize_url(original_url)
        except ValueError as exc:
            error = str(exc)
        else:
            code = generate_short_id()
            db = get_db()
            db.execute('INSERT INTO links (id, url) VALUES (?, ?)', (code, long_url))
            db.commit()
            short_url = url_for('redirect_link', code=code, _external=True)

    db = get_db()
    recent = db.execute(
        'SELECT id, url, visits FROM links ORDER BY created_at DESC LIMIT ?',
        (RECENT_LINKS_LIMIT,),
    ).fetchall()

    return render_template(
        'index.html',
        short_url=short_url,
        error=error,
        recent=recent,
        original_url=original_url,
    )


@app.route('/snxth')
def credit() -> str:
    return render_template('credit.html')


@app.route('/<code>')
def redirect_link(code: str):
    db = get_db()
    row = db.execute('SELECT url FROM links WHERE id = ?', (code,)).fetchone()
    if row:
        db.execute('UPDATE links SET visits = visits + 1 WHERE id = ?', (code,))
        db.commit()
        return redirect(row['url'])

    return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(error: Exception) -> tuple[str, int]:
    return render_template('404.html'), 404


if __name__ == '__main__':
    import os
    ensure_database()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
