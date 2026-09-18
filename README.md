# Sahu Tours & Travels

Flask + SQLAlchemy travel agency website with:
- Animated responsive customer website
- Tour packages and service pages
- Booking/enquiry form
- Admin login
- Package CRUD
- Admin password change
- PostgreSQL-ready deployment
- SQLite for local development

## Local
Windows:
1. `py -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python app.py`
5. Open `http://127.0.0.1:5000`

Admin:
- URL: `/admin/login`
- Username: 
- Password: 

Change the password immediately from the Admin Dashboard.

## Production
Set:
- `SECRET_KEY` to a long random value
- `DATABASE_URL` to your PostgreSQL connection string
Then run:
`gunicorn app:app`

The free Render web service is suitable for a low-cost launch, but it sleeps after inactivity. For persistent production data, use an external PostgreSQL service such as Supabase rather than a local SQLite file.
