# Mock Stock Exchange (CS50 Finance-inspired)

A Flask web application that simulates a stock trading platform. Users can register, log in, get real-time stock quotes, buy and sell shares, add cash to their account balance, and view their transaction history and current portfolio.

## Features
- **Authentication**: Register, log in, log out
- **Quote Lookup**: Get live stock quotes via `finance.cs50.io`
- **Portfolio**: View current holdings with live prices, cash balance, and grand total
- **Buy/Sell**: Execute trades with validation and balance checks
- **Cash Management**: Add cash to your account (`/cash` route)
- **History**: See a chronological ledger of all transactions

## Tech Stack
- **Backend**: Python, Flask, Flask-Session
- **Database**: SQLite (via CS50 `SQL` library)
- **HTTP**: `requests` for quote lookups
- **Frontend**: Jinja2 templates, Bootstrap 5

## Project Structure
```
finance/
  app.py               # Flask app with routes and business logic
  helpers.py           # Utilities: apology, login_required, lookup, usd
  finance.db           # SQLite database
  requirements.txt     # Python dependencies
  static/styles.css    # Custom styles
  templates/           # Jinja2 templates (layout, index, buy, sell, etc.)
```

## Database
The SQLite database (`finance.db`) includes the following tables:
- `users`: user accounts with `username`, password `hash`, and `cash` balance
- `portfolio`: per-user holdings (unique on `(user_id, symbol)`)
- `transactions`: immutable ledger of buys/sells with timestamp

Indexes exist for efficient lookups on users, symbols, and user_id fields.

Note: A rolling limit of 100 transactions per user is enforced by deleting the oldest record after the 100th insert.

## Key Routes
- `/` (GET): Portfolio dashboard
- `/quote` (GET/POST): Stock quote lookup
- `/buy` (GET/POST): Purchase shares
- `/sell` (GET/POST): Sell shares you own
- `/history` (GET): Transaction history
- `/cash` (GET/POST): Insert cash into your account
- `/register` (GET/POST): Create an account
- `/login` (GET/POST): Sign in
- `/logout` (GET): Sign out

## Setup
1) Clone the repository
```bash
git clone <your-repo-url>.git
cd "mock stock eschange site/finance"
```

2) Create and activate a virtual environment
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (cmd)
python -m venv .venv
.venv\Scripts\activate.bat
```

3) Install dependencies
```bash
pip install -r requirements.txt
```

4) Environment variables (development)
```bash
# Windows (cmd)
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

# Or PowerShell
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"
```

5) Initialize database (if starting fresh)
- The repo includes `finance.db`. If you want to reset it, delete the file and recreate using the schema in `requirements.txt` (see the commented schema section) or create tables via your preferred SQLite tool.

## Running the App
```bash
flask run
```
Then open `http://127.0.0.1:5000/` in your browser.

## Usage Notes
- Quotes are fetched from `https://finance.cs50.io/quote?symbol=...` via `helpers.lookup`.
- Currency values are formatted using the custom Jinja filter `usd`.
- The `/sell` route ensures you can only sell symbols you own and updates holdings accordingly, removing zero-share rows.
- The `/cash` route allows positive cash additions to the user’s balance.

## Screens (Templates)
- `index.html`: portfolio with cash and grand total
- `quote.html`: form and displayed quote results
- `buy.html` / `sell.html`: trading forms
- `history.html`: transaction ledger
- `login.html` / `register.html`: auth screens
- `apology.html`: error display helper

## Development Tips
- If you see “must provide …” or similar messages, they are rendered by the `apology` helper.
- Sessions are configured to use the filesystem; no external store is required in development.
- Be mindful of the 100-transaction rolling window when testing.

## Roadmap / Ideas
- Add unit tests for routes and helpers
- Paginate transaction history
- Add quote charting and intraday data
- Support conditional orders or watchlists
- Dockerize for easier setup

## Credits
- Inspired by Harvard’s CS50 Finance problem set
- Built with Flask, Bootstrap, and the CS50 `SQL` library

## License
MIT License. See `LICENSE` if included, or adapt as needed.


