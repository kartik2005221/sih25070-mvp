# SecureWipe — SIH Prototype

A working end-to-end demo of: **multi-pass secure erase → digitally signed
certificate (JSON + PDF) → independent third-party verification portal**,
matching the problem statement's core ask (secure wipe + tamper-proof cert +
verification), built as a Mobile/Web-friendly Flask app.

## What's real vs. simulated (be upfront about this in your pitch)

**Real:**
- Multi-pass overwrite (random → zero → random) + delete, actually performed on disk
- RSA-PSS-SHA256 digital signing of the certificate data
- Signature verification that correctly detects tampering (change one byte
  of the certificate and verification fails)
- JSON + PDF certificate generation
- A separate verification portal that only needs the certificate file, not
  access to the original device — this is the "third-party verification" requirement

**Simulated for demo safety (say this explicitly, it shows maturity, not weakness):**
- The wipe target is a sandboxed demo folder (`demo_target/`), not a raw disk
  partition. Real disk-level wiping (needed for full NIST SP 800-88 compliance,
  HPA/DCO hidden areas, SSD sector remapping) requires OS-level privileged
  block-device access, different on Windows/Linux/Android — that's genuinely
  a multi-week driver-level engineering effort, not something to fake in a demo.
- No bootable ISO/USB flow yet — that's a packaging/OS-image task, separate
  from proving the core pipeline works.

Framing it this way in your pitch is a strength: you're showing judges you
understand *why* those pieces are hard, rather than hand-waving a fake full
implementation.

## Setup (do this tonight)

```bash
cd sih-wipe-mvp
pip install flask cryptography reportlab
python3 app.py
```

Then open **http://localhost:5050** in a browser.

- The home page shows dummy sensitive-looking files (`bank_statements.pdf`,
  `personal_photos.dat`, etc. — filled with random bytes, not real data)
- Click **"Wipe & Certify This Device"** — watch it wipe live, then get a
  signed certificate you can download as PDF or JSON
- Click **"Verify this certificate"** to open the verification portal in a
  new tab, and upload the JSON certificate to see it confirmed as valid
- To demo tamper detection: open the downloaded JSON, change any value
  (e.g. `total_files`), save it, and upload that to `/verify` — it will
  correctly show **invalid**

Refreshing `/` regenerates a fresh batch of demo files so you can re-run
the wipe multiple times for rehearsal or during the live demo.

## Project structure

```
app.py              Flask routes: /, /wipe, /verify, /certificate/<id>.<fmt>
wipe_engine.py       Multi-pass overwrite + delete logic
cert_engine.py       RSA keypair mgmt, signing, verification, PDF rendering
templates/index.html One-click wipe UI
templates/verify.html Verification portal UI
keys/                 RSA keypair (auto-generated on first run)
demo_target/          Sandboxed folder that gets "wiped" (safe — dummy files)
certificates/         Generated JSON + PDF certificates land here
```

## Suggested pitch flow (2–3 min)

1. **Problem** (30s): e-waste stats, fear of data leaks preventing safe disposal
2. **Live demo** (60–90s): open the app, click wipe, show the live log, download
   the PDF certificate, then open the verification portal and prove it's valid
3. **Tamper demo** (20s): show an edited certificate get rejected — this is
   your strongest visual moment, use it
4. **Architecture + compliance slide**: how this maps to NIST SP 800-88, and
   what "Phase 2" (raw disk access, bootable USB, Android support) looks like
5. **Close**: circular economy impact — confidence to recycle instead of hoard

## Honest answers for judge Q&A

- **"How do you handle SSD wear-leveling?"** — Overwrite-based wiping alone
  can't guarantee this because the SSD controller remaps blocks; the real
  fix is issuing ATA Secure Erase / NVMe Format commands directly to the
  drive controller, which is next-phase, privileged, hardware-specific work.
- **"Why not wipe a real disk in the demo?"** — Safety and reproducibility;
  the cryptographic signing/verification pipeline is identical either way,
  only the storage-access layer would change.
- **"Is the signature scheme production-grade?"** — RSA-PSS-SHA256 is a
  standard, secure choice; production would add a proper PKI/certificate
  chain rather than a single local keypair, so any verifier can trust the
  issuing authority without pre-sharing a key file.
