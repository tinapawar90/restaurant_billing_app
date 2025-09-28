# Restaurant Billing App (Flask)

A simple restaurant billing web app with full menu management and persistent menu storage (`menu.json`).

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
## Deploy to Heroku / Render
- Heroku: create app, push repo, set `FLASK_ENV=production`, use Procfile (web: gunicorn app:app)
- Render: create web service, build with `gunicorn app:app`, set start command `gunicorn app:app`
