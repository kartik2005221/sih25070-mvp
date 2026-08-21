# SIH - Secure Data Wipe & Certification Simulators

This repository contains two data wiping and certification simulation projects:

1. **`sih-wipe-mvp`**: Full-featured Flask-based Secure Data Erasure MVP with NIST 800-88 / DoD 5220.22-M wiping simulations, cryptographic signature generation (RSA-2048 / SHA-256), tamper-evident QR code embedding, PDF certificate generation, and an online verification portal.
2. **`sih-data-wipe-simulation`**: Interactive terminal & web-based simulation demonstrating multi-pass data sanitization algorithms, block verification, and real-time wiping progress.

## Structure

```
.
├── sih-wipe-mvp/               # Flask MVP with crypto verification & PDF cert engine
│   ├── app.py                  # Web application & API routes
│   ├── cert_engine.py          # RSA digital signature & PDF certificate generator
│   ├── wipe_engine.py          # Multi-standard data wipe simulation engine
│   ├── templates/              # Dashboard & certificate verification UI
│   └── requirements.txt        # Python dependencies
└── sih-data-wipe-simulation/   # Interactive simulation demos
    ├── terminal_demo.py        # Terminal visualizer
    ├── index.html              # Web visualizer
    └── README.md
```
