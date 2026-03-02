import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# ----------------------------
# Configuration
# ----------------------------
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# Helper Function
# ----------------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        # Clear action
        if action == "clear":
            return redirect(url_for("index"))

        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            file_info = {
                "filename": filename,
                "size_kb": round(os.path.getsize(filepath) / 1024, 2),
                "type": filename.split('.')[-1]
            }

            # Submit action
            if action == "submit":
                flash("File submitted successfully.")

            # Read action (only text)
            if action == "read" and filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()

            # View action
            if action == "view":
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    preview_type = "image"
                elif filename.lower().endswith(".pdf"):
                    preview_type = "pdf"

            return render_template(
                "index.html",
                file_info=file_info,
                file_content=file_content,
                preview_type=preview_type
            )

        else:
            flash("File type not allowed.")
            return redirect(request.url)

    return render_template("index.html")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)