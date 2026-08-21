import os
import json
import uuid
import random
import shutil

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for

import cert_engine
import wipe_engine

BASE_DIR = os.path.dirname(__file__)
DEMO_TARGET_DIR = os.path.join(BASE_DIR, "demo_target")
CERT_DIR = os.path.join(BASE_DIR, "certificates")

app = Flask(__name__)
cert_engine.ensure_keypair()
os.makedirs(CERT_DIR, exist_ok=True)


def reset_demo_files():
    """(Re)create a handful of dummy files in demo_target/ so the demo can be re-run."""
    shutil.rmtree(DEMO_TARGET_DIR, ignore_errors=True)
    os.makedirs(DEMO_TARGET_DIR, exist_ok=True)
    sample_contents = {
        "personal_photos.dat": os.urandom(20000),
        "bank_statements.pdf": os.urandom(35000),
        "browser_saved_passwords.db": os.urandom(8000),
        "college_documents.docx": os.urandom(15000),
        "whatsapp_chat_backup.db": os.urandom(50000),
    }
    for name, content in sample_contents.items():
        with open(os.path.join(DEMO_TARGET_DIR, name), "wb") as f:
            f.write(content)


@app.route("/")
def index():
    reset_demo_files()
    files = os.listdir(DEMO_TARGET_DIR)
    device_id = f"DEMO-LAPTOP-{random.randint(1000, 9999)}"
    return render_template("index.html", files=files, device_id=device_id)


@app.route("/wipe", methods=["POST"])
def wipe():
    device_id = request.json.get("device_id", "DEMO-DEVICE-001")

    if not os.path.isdir(DEMO_TARGET_DIR) or not os.listdir(DEMO_TARGET_DIR):
        reset_demo_files()

    wipe_result = wipe_engine.wipe_directory(DEMO_TARGET_DIR, device_id)
    wipe_result["certificate_id"] = cert_engine.make_certificate_id()

    cert = cert_engine.build_certificate_json(wipe_result)

    json_path = os.path.join(CERT_DIR, f"{cert['certificate_id']}.json")
    pdf_path = os.path.join(CERT_DIR, f"{cert['certificate_id']}.pdf")

    with open(json_path, "w") as f:
        json.dump(cert, f, indent=2)

    cert_engine.certificate_to_pdf(cert, pdf_path)

    return jsonify({
        "certificate": cert,
        "json_url": url_for("download_certificate", cert_id=cert["certificate_id"], fmt="json"),
        "pdf_url": url_for("download_certificate", cert_id=cert["certificate_id"], fmt="pdf"),
    })


@app.route("/certificate/<cert_id>.<fmt>")
def download_certificate(cert_id, fmt):
    path = os.path.join(CERT_DIR, f"{cert_id}.{fmt}")
    if not os.path.exists(path):
        return "Not found", 404
    return send_file(path, as_attachment=True)


@app.route("/verify", methods=["GET"])
def verify_page():
    return render_template("verify.html")


@app.route("/verify", methods=["POST"])
def verify_certificate():
    if "certfile" not in request.files:
        return jsonify({"valid": False, "error": "No file uploaded"}), 400

    file = request.files["certfile"]
    try:
        cert = json.loads(file.read().decode("utf-8"))
    except Exception:
        return jsonify({"valid": False, "error": "Could not parse JSON"}), 400

    signature = cert.pop("signature", None)
    cert.pop("signature_algorithm", None)

    if not signature:
        return jsonify({"valid": False, "error": "No signature field found in certificate"})

    is_valid = cert_engine.verify_record(cert, signature)

    # extra tamper check: does a certificate with this ID actually exist on our server?
    cert_id = cert.get("certificate_id", "")
    server_copy_path = os.path.join(CERT_DIR, f"{cert_id}.json")
    server_match = False
    if os.path.exists(server_copy_path):
        with open(server_copy_path) as f:
            server_cert = json.load(f)
        server_match = server_cert.get("signature") == signature

    return jsonify({
        "valid": is_valid,
        "server_record_found": os.path.exists(server_copy_path),
        "server_signature_match": server_match,
        "certificate_id": cert_id,
        "device_id": cert.get("device_id"),
        "status": cert.get("status"),
    })


@app.route("/public-key")
def public_key():
    return cert_engine.get_public_key_pem(), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
