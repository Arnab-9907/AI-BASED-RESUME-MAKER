import json
import os
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import wraps
from urllib import error, request

from docx import Document
from flask import Flask, jsonify, request as flask_request, send_file
from PIL import Image, ImageDraw, ImageFont
import jwt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"
JWT_SECRET = os.environ.get("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGO = "HS256"
JWT_EXP_HOURS = 24

@app.route("/")
def index():
    return send_file('src/index.html')


def read_users():
    if not USERS_FILE.exists():
        return []
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def create_token(email):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXP_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_auth_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def require_auth(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        auth_header = flask_request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header."}), 401
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_auth_token(token)
            flask_request.user_email = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired. Please login again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token. Please login again."}), 401
        return route(*args, **kwargs)
    return wrapper


@app.post("/api/auth/register")
def register():
    data = flask_request.get_json(silent=True) or {}
    full_name = (data.get("fullName") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not full_name or not email or not password:
        return jsonify({"error": "Full name, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    users = read_users()
    if any(user.get("email") == email for user in users):
        return jsonify({"error": "User already exists with this email."}), 409

    users.append({
        "fullName": full_name,
        "email": email,
        "passwordHash": generate_password_hash(password),
    })
    write_users(users)

    token = create_token(email)
    return jsonify({
        "token": token,
        "user": {"fullName": full_name, "email": email}
    }), 201


@app.post("/api/auth/login")
def login():
    data = flask_request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = next((item for item in read_users() if item.get("email") == email), None)
    if not user or not check_password_hash(user.get("passwordHash", ""), password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_token(email)
    return jsonify({
        "token": token,
        "user": {"fullName": user.get("fullName", ""), "email": email}
    })


@app.get("/api/auth/me")
@require_auth
def me():
    user = next((item for item in read_users() if item.get("email") == flask_request.user_email), None)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": {"fullName": user.get("fullName", ""), "email": user.get("email", "")}})


def build_prompt(data):
    return f"""
Create a professional, ATS-friendly resume in plain text.
Use strong action verbs, concise bullet points, and quantifiable impact where possible.
Do not invent facts beyond what is provided.

Candidate Information:
- Full Name: {data.get("fullName", "")}
- Email: {data.get("email", "")}
- Phone: {data.get("phone", "")}
- Location: {data.get("location", "")}
- LinkedIn: {data.get("linkedin", "")}
- Portfolio/GitHub: {data.get("portfolio", "")}
- Target Role: {data.get("targetRole", "")}

- Professional Summary Input:
{data.get("summary", "")}

- Skills:
{data.get("skills", "")}

- Work Experience:
{data.get("experience", "")}

- Education:
{data.get("education", "")}

- Projects:
{data.get("projects", "")}

- Certifications:
{data.get("certifications", "")}

Return only the final resume content in this exact structure:
1) Name + contact line
2) Professional Summary
3) Key Skills
4) Work Experience
5) Projects
6) Education
7) Certifications
""".strip()


def fallback_resume(data):
    name = data.get("fullName", "Your Name")
    contact_parts = [data.get("email", ""), data.get("phone", ""), data.get("location", "")]
    contact = " | ".join([part for part in contact_parts if part])
    links = " | ".join([link for link in [data.get("linkedin", ""), data.get("portfolio", "")] if link])

    return f"""
{name}
{contact}
{links}

PROFESSIONAL SUMMARY
{data.get("summary", "Motivated professional seeking opportunities to create impact.")}

KEY SKILLS
{data.get("skills", "List your top technical and soft skills.")}

WORK EXPERIENCE
{data.get("experience", "Add your role, company, dates, and achievements with metrics.")}

PROJECTS
{data.get("projects", "Add your notable projects, tech stack, and outcomes.")}

EDUCATION
{data.get("education", "Add degree, institution, and graduation year.")}

CERTIFICATIONS
{data.get("certifications", "Add certifications if available.")}
""".strip()


def generate_with_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            }
        ]
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            parsed = json.loads(response.read().decode("utf-8"))
        return parsed["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (error.URLError, error.HTTPError, KeyError, IndexError, json.JSONDecodeError):
        return None


@app.post("/api/generate-resume")
@require_auth
def generate_resume():
    data = flask_request.get_json(silent=True) or {}

    if not data.get("fullName") or not data.get("targetRole"):
        return jsonify(
            {"error": "Please provide at least full name and target role."}
        ), 400

    prompt = build_prompt(data)
    ai_result = generate_with_gemini(prompt)

    if ai_result:
        return jsonify({"resume": ai_result, "source": "gemini"})

    return jsonify({"resume": fallback_resume(data), "source": "fallback"})


def sanitize_filename(name):
    cleaned = "".join(char for char in name if char.isalnum() or char in ("-", "_", " ")).strip()
    return (cleaned or "resume").replace(" ", "_").lower()


def render_pdf(text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 42
    pdf.setFont("Helvetica", 11)

    for line in text.splitlines() or [""]:
        if y < 42:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 42
        pdf.drawString(42, y, line[:110])
        y -= 16

    pdf.save()
    buffer.seek(0)
    return buffer


def render_docx(text):
    doc = Document()
    for line in text.splitlines() or [""]:
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def render_image(text, image_format):
    width, height = 1240, 1754
    image = Image.new("RGB", (width, height), color=(250, 251, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    x, y = 56, 56
    max_width = width - (x * 2)

    for line in text.splitlines() or [""]:
        current = ""
        for word in line.split(" "):
            test = (current + " " + word).strip()
            if draw.textlength(test, font=font) <= max_width:
                current = test
            else:
                draw.text((x, y), current, fill=(17, 24, 39), font=font)
                y += 22
                current = word
                if y > height - 56:
                    break
        if y > height - 56:
            break
        draw.text((x, y), current, fill=(17, 24, 39), font=font)
        y += 24
        if y > height - 56:
            break

    buffer = BytesIO()
    image.save(buffer, format=image_format)
    buffer.seek(0)
    return buffer


@app.post("/api/download-resume")
@require_auth
def download_resume():
    payload = flask_request.get_json(silent=True) or {}
    text = (payload.get("resume") or "").strip()
    file_format = (payload.get("format") or "").lower()
    base_name = sanitize_filename(payload.get("fileName", "resume"))

    if not text:
        return jsonify({"error": "Resume content is empty. Generate resume first."}), 400

    if file_format == "pdf":
        return send_file(
            render_pdf(text),
            as_attachment=True,
            download_name=f"{base_name}.pdf",
            mimetype="application/pdf",
        )

    if file_format == "docx":
        return send_file(
            render_docx(text),
            as_attachment=True,
            download_name=f"{base_name}.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    if file_format == "png":
        return send_file(
            render_image(text, "PNG"),
            as_attachment=True,
            download_name=f"{base_name}.png",
            mimetype="image/png",
        )

    if file_format == "jpg":
        return send_file(
            render_image(text, "JPEG"),
            as_attachment=True,
            download_name=f"{base_name}.jpg",
            mimetype="image/jpeg",
        )

    return jsonify({"error": "Unsupported format. Use pdf, docx, jpg, or png."}), 400

def main():
    app.run(port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    main()
