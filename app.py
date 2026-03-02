import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# ----------------------------
# Configuration
# ----------------------------
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'pdf'}

# Use /tmp for Render (ephemeral storage)
UPLOAD_FOLDER = "/uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# Helper Function
# ----------------------------
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    file_info = None
    file_content = None
    preview_type = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "clear":
            return redirect(url_for("index"))

        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("File type not allowed.")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        file_info = {
            "filename": filename,
            "size_kb": round(os.path.getsize(filepath) / 1024, 2),
            "type": filename.split(".")[-1]
        }

        if action == "submit":
            flash("File submitted successfully.")

        if action == "read" and filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()

        if action == "view":
            if filename.lower().endswith(("png", "jpg", "jpeg")):
                preview_type = "image"
            elif filename.lower().endswith("pdf"):
                preview_type = "pdf"

        return render_template(
            "index.html",
            file_info=file_info,
            file_content=file_content,
            preview_type=preview_type
        )

    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ----------------------------
# Production Entry
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
