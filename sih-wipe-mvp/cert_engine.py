"""
cert_engine.py
Handles: RSA keypair management, signing wipe records, generating
tamper-evident certificates in JSON + PDF, and verifying signatures.
"""

import json
import base64
import os
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")


def ensure_keypair():
    """Generate an RSA keypair once and persist it, like a device/authority key."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    if os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))


def _load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def _load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def _canonical_bytes(record: dict) -> bytes:
    """Deterministic JSON encoding so sign/verify always hash the same bytes."""
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_record(record: dict) -> str:
    """Sign a wipe record (dict, WITHOUT the 'signature' key) and return base64 signature."""
    private_key = _load_private_key()
    signature = private_key.sign(
        _canonical_bytes(record),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_record(record: dict, signature_b64: str) -> bool:
    """Verify a record dict (without 'signature' key) against a base64 signature."""
    public_key = _load_public_key()
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            _canonical_bytes(record),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def get_public_key_pem() -> str:
    with open(PUBLIC_KEY_PATH, "r") as f:
        return f.read()


def build_certificate_json(wipe_result: dict) -> dict:
    """
    wipe_result must contain: certificate_id, device_id, wipe_method,
    files_wiped (list), total_files, total_bytes, start_time, end_time, status
    Returns the full certificate dict including the signature.
    """
    record = {k: wipe_result[k] for k in (
        "certificate_id", "device_id", "wipe_method", "files_wiped",
        "total_files", "total_bytes", "start_time", "end_time", "status",
        "software",
    )}
    signature = sign_record(record)
    full_cert = dict(record)
    full_cert["signature"] = signature
    full_cert["signature_algorithm"] = "RSA-PSS-SHA256"
    return full_cert


def certificate_to_pdf(cert: dict, output_path: str):
    """Render a signed certificate dict to a formatted PDF file."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=20 * mm, bottomMargin=20 * mm,
                             leftMargin=20 * mm, rightMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CertTitle", parent=styles["Title"], fontSize=20, spaceAfter=4,
        textColor=colors.HexColor("#1a5632"),
    )
    subtitle_style = ParagraphStyle(
        "CertSubtitle", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#555555"), spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontSize=12,
        textColor=colors.HexColor("#1a5632"), spaceBefore=14, spaceAfter=6,
    )
    mono_style = ParagraphStyle(
        "Mono", parent=styles["Normal"], fontName="Courier", fontSize=7,
        textColor=colors.HexColor("#333333"),
    )

    story = []
    story.append(Paragraph("Certificate of Secure Data Erasure", title_style))
    story.append(Paragraph(
        "Issued in alignment with NIST SP 800-88 media sanitization guidelines",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#1a5632"), thickness=1.2))
    story.append(Spacer(1, 10))

    status_color = colors.HexColor("#1a7a3c") if cert["status"] == "SUCCESS" else colors.red
    status_style = ParagraphStyle("Status", parent=styles["Normal"], fontSize=13,
                                   textColor=status_color, spaceAfter=10)
    story.append(Paragraph(f"Status: <b>{cert['status']}</b>", status_style))

    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=9.5, leading=12)
    label_style = ParagraphStyle("CellLabel", parent=cell_style, fontName="Helvetica-Bold")

    def row(label, value):
        return [Paragraph(label, label_style), Paragraph(str(value), cell_style)]

    summary_data = [
        row("Certificate ID", cert["certificate_id"]),
        row("Device ID", cert["device_id"]),
        row("Wipe Method", cert["wipe_method"]),
        row("Files Wiped", cert["total_files"]),
        row("Total Bytes Sanitized", f"{cert['total_bytes']:,} bytes"),
        row("Start Time (UTC)", cert["start_time"]),
        row("End Time (UTC)", cert["end_time"]),
        row("Issued By", cert["software"]),
    ]
    table = Table(summary_data, colWidths=[50 * mm, 110 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f7f3")),
    ]))
    story.append(table)

    story.append(Paragraph("Files Sanitized", section_style))
    file_rows = [["File", "Size (bytes)", "Passes"]]
    for f in cert["files_wiped"][:15]:
        file_rows.append([f["name"], str(f["size_bytes"]), str(f["passes"])])
    if len(cert["files_wiped"]) > 15:
        file_rows.append(["...", "...", "..."])
    file_table = Table(file_rows, colWidths=[90 * mm, 40 * mm, 30 * mm])
    file_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5632")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9f7")]),
    ]))
    story.append(file_table)

    story.append(Paragraph("Digital Signature (tamper-evident)", section_style))
    story.append(Paragraph(
        "This certificate is cryptographically signed. Any modification to the data "
        "above will invalidate the signature below. Verify at the issuing "
        "authority's verification portal by uploading the accompanying JSON file.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Algorithm: {cert['signature_algorithm']}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(cert["signature"], mono_style))

    doc.build(story)


def make_certificate_id() -> str:
    import uuid
    return f"WIPE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
