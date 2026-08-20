import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
database_url = os.environ.get("DATABASE_URL", "sqlite:///sahu_tours.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="Tour Package")
    duration = db.Column(db.String(80), default="Custom")
    price = db.Column(db.String(80), default="On Request")
    description = db.Column(db.Text, default="")
    image = db.Column(db.String(500), default="")
    featured = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(160))
    destination = db.Column(db.String(160))
    travel_date = db.Column(db.String(40))
    people = db.Column(db.Integer, default=1)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

SERVICES = [
    "Private tours","Adventure tours","Bus tours","Campus tours","Educational tours",
    "Group tours","Historical tours","Sightseeing tours","Bus on rent",
    "AC/Non-AC Sleeper Bus on Rent","AC/Non-AC Seater Bus on Rent"
]

SEED_PACKAGES = [
    ("Nepal Tour Package","International","Custom","On Request"),
    ("Chardham Yatra Package","Pilgrimage","Custom","On Request"),
    ("Bastar Tour Package","Domestic","Custom","On Request"),
    ("Ujjain Mahkaal Tour Package","Pilgrimage","Custom","On Request"),
    ("Gangasagar Tirthyatra","Pilgrimage","Custom","On Request"),
    ("Ayodhya, Mathura & Vrindavan Tour","Pilgrimage","Custom","On Request"),
    ("Banaras / Kashi Vishwanath Tour","Pilgrimage","Custom","On Request"),
    ("Prayagraj Tour","Domestic","Custom","On Request"),
    ("Nepal Muktinath Tour Package","International","Custom","On Request"),
    ("Shirdi & Nasik Tour","Pilgrimage","Custom","On Request"),
    ("Khatushyam Rajasthan Tour","Pilgrimage","Custom","On Request"),
    ("Gujarat Somnath Jyotirling Tour","Pilgrimage","Custom","On Request"),
    ("Rameshwaram, Tirupati Balaji & Kerala Tour","South India","Custom","On Request"),
    ("8 Jyotirling Tour Package","Pilgrimage","Custom","On Request"),
    ("Nepal, Kathmandu, Kamakhya Devi & Darjeeling Tour","Multi-Destination","Custom","On Request"),
    ("Amarnath Yatra","Pilgrimage","Custom","On Request"),
    ("Vaishno Devi Yatra","Pilgrimage","Custom","On Request"),
    ("Gaya Ji Yatra","Pilgrimage","Custom","On Request"),
    ("Mumbai Goa Tour Package","Domestic","Custom","On Request"),
    ("Visakhapatnam & Araku Valley Tour","Domestic","Custom","On Request"),
    ("Kumbh Mela Yatra","Pilgrimage","Custom","On Request"),
    ("संपूर्ण भारत तीर्थयात्रा","Pilgrimage","Custom","On Request"),
    ("दक्षिण भारत यात्रा","South India","Custom","On Request"),
    ("उत्तर भारत यात्रा","North India","Custom","On Request"),
    ("Kashmir Tour Package","Domestic","Custom","On Request"),
]

def seed():
    db.create_all()
    if not Admin.query.filter_by(username="admin").first():
        db.session.add(Admin(username="admin", password_hash=generate_password_hash("1234")))
    if Package.query.count() == 0:
        for title, category, duration, price in SEED_PACKAGES:
            db.session.add(Package(
                title=title, category=category, duration=duration, price=price,
                description=f"Plan your {title} with Sahu Tours & Travels. Contact us for itinerary, transport, hotel and group pricing.",
                featured=title in ["Nepal Tour Package","Chardham Yatra Package","Kashmir Tour Package"]
            ))
    db.session.commit()

with app.app_context():
    seed()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_globals():
    return {
        "company_name": "Sahu Tours & Travels",
        "phone": "098264 86235",
        "phone_href": "+919826486235",
        "address": "Street No. 5, Kasaridih - Borsi Rd, behind Rao Cortege, Bhilai, Durg, Chhattisgarh 491001",
        "services": SERVICES
    }

@app.route("/")
def home():
    featured = Package.query.filter_by(featured=True).limit(6).all()
    return render_template("index.html", featured=featured)

@app.route("/packages")
def packages():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = Package.query
    if q:
        query = query.filter(Package.title.ilike(f"%{q}%"))
    if category:
        query = query.filter_by(category=category)
    items = query.order_by(Package.id.desc()).all()
    categories = [x[0] for x in db.session.query(Package.category).distinct().all()]
    return render_template("packages.html", packages=items, categories=categories, q=q, category=category)

@app.route("/package/<int:package_id>")
def package_detail(package_id):
    item = Package.query.get_or_404(package_id)
    return render_template("package_detail.html", item=item)

@app.route("/services")
def services_page():
    return render_template("services.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        phone = request.form.get("phone","").strip()
        if not name or not phone:
            flash("Please enter your name and mobile number.", "error")
            return redirect(url_for("booking"))
        b = Booking(
            name=name,
            phone=phone,
            email=request.form.get("email","").strip(),
            destination=request.form.get("destination","").strip(),
            travel_date=request.form.get("travel_date","").strip(),
            people=int(request.form.get("people") or 1),
            message=request.form.get("message","").strip()
        )
        db.session.add(b)
        db.session.commit()
        flash("Enquiry received! Sahu Tours & Travels will contact you shortly.", "success")
        return redirect(url_for("booking"))
    return render_template("booking.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    items = Package.query.order_by(Package.id.desc()).all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin_dashboard.html", packages=items, bookings=bookings)

@app.route("/admin/package/new", methods=["GET", "POST"])
@login_required
def admin_package_new():
    if request.method == "POST":
        item = Package(
            title=request.form.get("title","").strip(),
            category=request.form.get("category","Tour Package").strip(),
            duration=request.form.get("duration","Custom").strip(),
            price=request.form.get("price","On Request").strip(),
            description=request.form.get("description","").strip(),
            image=request.form.get("image","").strip(),
            featured=request.form.get("featured") == "on"
        )
        db.session.add(item)
        db.session.commit()
        flash("Package added.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_package_form.html", item=None)

@app.route("/admin/package/<int:package_id>/edit", methods=["GET", "POST"])
@login_required
def admin_package_edit(package_id):
    item = Package.query.get_or_404(package_id)
    if request.method == "POST":
        item.title = request.form.get("title","").strip()
        item.category = request.form.get("category","Tour Package").strip()
        item.duration = request.form.get("duration","Custom").strip()
        item.price = request.form.get("price","On Request").strip()
        item.description = request.form.get("description","").strip()
        item.image = request.form.get("image","").strip()
        item.featured = request.form.get("featured") == "on"
        db.session.commit()
        flash("Package updated.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_package_form.html", item=item)

@app.route("/admin/package/<int:package_id>/delete", methods=["POST"])
@login_required
def admin_package_delete(package_id):
    item = Package.query.get_or_404(package_id)
    db.session.delete(item)
    db.session.commit()
    flash("Package deleted.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def admin_password():
    admin = db.session.get(Admin, session["admin_id"])
    if request.method == "POST":
        old = request.form.get("old_password","")
        new = request.form.get("new_password","")
        confirm = request.form.get("confirm_password","")
        if not check_password_hash(admin.password_hash, old):
            flash("Current password is incorrect.", "error")
        elif len(new) < 6:
            flash("New password must be at least 6 characters.", "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        else:
            admin.password_hash = generate_password_hash(new)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_password.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
