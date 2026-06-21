from flask import Flask, render_template, request, redirect, url_for, flash, send_file, after_this_request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User
import os 
from werkzeug.utils import secure_filename

from models import db, User, File, Activity
import secrets
from s3_service import (
    upload_file_to_s3,
    get_file_url,
    delete_file_from_s3
)

from encryption import (
    encrypt_file,
    decrypt_file
)

from s3_service import s3
from config import Config
import secrets
from flask_dance.contrib.google import make_google_blueprint, google
  
app = Flask(__name__)

app.config.from_object(Config)

google_bp = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"]
)

app.register_blueprint(google_bp, url_prefix="/login")

print(app.config.get("SQLALCHEMY_DATABASE_URL"))

app.config["UPLOAD_FOLDER"] = "uploads"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

#---------------------REGISTER-------------------#

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:

            flash("User already exists")

            return redirect("/register")

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")

        return redirect("/login")

    return render_template("register.html")

#----------------LOGIN-------------------#

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect("/dashboard")

        flash("Invalid Email or Password")

    return render_template("login.html")

#---------------------GOOGLE LOGIN ROUTE-------------------#

@app.route("/google-login")
def google_login():

    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    info = resp.json()

    email = info["email"]
    name = info["name"]

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=name,
            email=email
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)

    return redirect(url_for("dashboard"))

#-----------------DASHBOARD-------------------------#

@app.route("/dashboard")
@login_required
def dashboard():

    search = request.args.get("search", "")

    files = File.query.filter(
        File.user_id == current_user.id,
        File.filename.contains(search)
    ).all()

    total_files = len(files)

    total_storage = sum(
        file.filesize for file in files
    )

    total_storage_mb = round(
        total_storage / (1024 * 1024),
        2
    )

    storage_percentage = round(
        (total_storage_mb / 1024) * 100,
        2
    )

    recent_files = File.query.filter_by(
        user_id=current_user.id
    ).order_by(
        File.upload_date.desc()
    ).limit(5).all()

    shared_files = File.query.filter(
        File.user_id == current_user.id,
        File.share_token.isnot(None)
    ).count()

    activities = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(

        Activity.timestamp.desc()
    ).limit(10).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        files=files,
        activities=activities,
        total_files=total_files,
        total_storage_mb=total_storage_mb,
        storage_percentage=storage_percentage,
        search=search
    )

#----------------- ADMIN DASHBOARD---------------------#

@app.route("/admin")
@login_required
def admin():

    if not current_user.is_admin:
        flash("Access Denied!")
        return redirect(url_for("dashboard"))

    users = User.query.all()
    files = File.query.all()

    total_users = User.query.count()
    total_files = File.query.count()

    total_storage = (
        db.session.query(
            db.func.sum(File.filesize)
        ).scalar() or 0
    )

    activities = Activity.query.order_by(
     Activity.timestamp.desc()
    ).limit(20).all()

    user_storage = []

    for user in users:
        storage = (
        db.session.query(
            db.func.sum(File.filesize)
        )
        .filter(File.user_id == user.id)
        .scalar() or 0
    )

    user_storage.append({
        "username": user.username,
        "storage": round(storage / (1024 * 1024), 2)
    })


    return render_template(
       "admin.html",
       users=users,
       files=files,
       activities=activities,
       total_users=total_users,
       total_files=total_files,
       total_storage=total_storage,
       user_storage=user_storage
    )

#-----------------ADMIN DELETE USER----------------#

@app.route("/admin/delete-user/<int:user_id>")
@login_required
def delete_user(user_id):

    if not current_user.is_admin:
        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(user_id)

    if user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for("admin"))

#-------------------- ADMIN DELETE FILE FEATURE---------------#

@app.route("/admin/delete-file/<int:file_id>")
@login_required
def admin_delete_file(file_id):

    if not current_user.is_admin:
        return redirect(url_for("dashboard"))

    file = File.query.get_or_404(file_id)

    delete_file_from_s3(file.s3_key)

    db.session.delete(file)
    db.session.commit()

    return redirect(url_for("admin"))

#------------------upload-------------------#

@app.route("/upload", methods=["POST"])
@login_required
def upload_file():

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return redirect("/dashboard")

    filename = secure_filename(
        uploaded_file.filename
    )

    existing = File.query.filter_by(
        user_id=current_user.id,
        original_filename=filename
    ).order_by(
        File.version.desc()
    ).first()

    version = 1

    if existing:
        version = existing.version + 1

    name, ext = os.path.splitext(filename)

    stored_filename = (
        f"{name}_v{version}{ext}"
    )

    stored_filename = f"{name}_v{version}{ext}"

    filepath = os.path.join(
     app.config["UPLOAD_FOLDER"],
     stored_filename
    )

    # Save locally first
    uploaded_file.save(filepath)

    # Get original file size
    filesize = os.path.getsize(filepath)

    # Encrypt the file
    encrypt_file(filepath)

    # Upload encrypted file
    with open(filepath, "rb") as f:
      upload_file_to_s3(
        f,
        stored_filename
    )

   # Remove temporary local file
    os.remove(filepath)

    new_file = File(
      filename=stored_filename,
      original_filename=filename,
      s3_key=stored_filename,
      filesize=filesize,
      version=version,
      user_id=current_user.id
    )

    db.session.add(new_file)
    db.session.commit()

    activity = Activity(
    action="Uploaded file",
    user_id=current_user.id
)

    db.session.add(activity)
    db.session.commit() 

    return redirect("/dashboard")

#-----------------Download---------------------#

@app.route("/download/<int:file_id>")
@login_required
def download_file(file_id):

    file = File.query.get_or_404(file_id)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    s3.download_file(
        Config.S3_BUCKET,
        file.s3_key,
        filepath
    )

    decrypt_file(filepath)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(filepath)
        except:
            pass
        return response
    
    activity = Activity(
      action="Downloaded",
      filename=file.filename,
      user_id=current_user.id
    )

    db.session.add(activity)
    db.session.commit()

    return send_file(
        filepath,
        as_attachment=True,
        download_name=file.original_filename
    )

#---------------------PREVIEW-----------------#

@app.route("/preview/<int:file_id>")
@login_required
def preview_file(file_id):

    file = File.query.get_or_404(file_id)

    url = get_file_url(file.s3_key)

    # If image or pdf → show preview
    if file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        return render_template("preview_image.html", url=url)

    if file.filename.lower().endswith(".pdf"):
        return render_template("preview_pdf.html", url=url)

    # fallback
    return redirect(url)

#----------------------SHARE-----------------#

@app.route("/share/<int:file_id>")
@login_required
def share_file(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect("/dashboard")

    if not file.share_token:
        file.share_token = secrets.token_urlsafe(16)
        db.session.commit()

    share_link = url_for(
        "public_file",
        token=file.share_token,
        _external=True
    )

    flash(f"Share Link: {share_link}")

    activity = Activity(
       action="Shared",
       filename=file.filename,
       user_id=current_user.id
    )

    db.session.add(activity)
    db.session.commit()

    return redirect("/dashboard")

#---------------------PUBLIC--------------#

@app.route("/shared/<token>")
def public_file(token):

    file = File.query.filter_by(
        share_token=token
    ).first_or_404()

    url = get_file_url(
        file.s3_key
    )

    return redirect(url)


#-----------------------delete route--------------------------#

@app.route("/delete/<int:file_id>")
@login_required
def delete_file(file_id):

    file = File.query.get_or_404(file_id)

    delete_file_from_s3(
     file.s3_key
    )

    db.session.delete(file)
    db.session.commit()

    activity = Activity(
      action="Deleted",
      filename=file.filename,
      user_id=current_user.id
    )

    db.session.add(activity)
    db.session.commit()

    return redirect("/dashboard")


#------------------- LOGOUT-----------------#

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)