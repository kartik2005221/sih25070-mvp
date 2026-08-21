# 🚀 How to Win SIH 2025: Data Sanitization & Forensic Recovery Simulation

**Problem Statement:** Design and prototype a secure, cross-platform data wiping application (Ministry of Mines / JNARDDC).  
**Purpose of this Simulation:** To demonstrate to judges and presenters **WHY** standard file deletion fails, **HOW** forensic tools recover "deleted" files, and **HOW** your SIH tool securely wipes sectors and generates tamper-proof audit certificates according to **NIST SP 800-88**.

---

## 💻 How to Run on Your Laptop

### Option 1: Interactive Web UI Simulation (Recommended for Presentation)
1. Navigate to the project directory:
   ```bash
   cd /home/kartik/sih-data-wipe-simulation
   ```
2. Launch a local web server (using Python):
   ```bash
   python3 -m http.server 8080
   ```
3. Open your web browser (Chrome/Firefox/Edge) and go to:
   ```text
   http://localhost:8080
   ```
   *(Or simply double-click `index.html` to open it directly in any browser!)*

---

### Option 2: Interactive Terminal / CLI Demo (For Tech-Savvy Judges)
If the judges want to see a low-level terminal demonstration:
```bash
python3 /home/kartik/sih-data-wipe-simulation/terminal_demo.py
```

---

## 🎯 4-Step Presentation Walkthrough for Presenters

| Step | Action in Demo | Presenter Script / What to Say to Judges |
| :--- | :--- | :--- |
| **Step 1: Normal State** | Click **"Load Sample Files"** | *"Here we see sensitive user data (Aadhaar KYC PDF, Bank Passbook, Passwords) saved on physical disk sectors. The operating system file table (NTFS MFT / Inodes) points directly to these memory sectors."* |
| **Step 2: OS Flaw (The Illusion)** | Click **"Shift + Delete Files"** | *"When a user empties the Recycle Bin or runs `rm`, the OS performs a LOGICAL deletion. It only changes a single flag in the File Table to 'unallocated'. Notice the disk map—THE RAW CONFIDENTIAL BYTES ARE STILL 100% INTACT ON DISK!"* |
| **Step 3: Forensic Attack** | Click **"Run Forensic Recovery"** | *"An attacker or dishonest second-hand device buyer can run forensic carvers (like Autopsy/SleuthKit). Because the sectors were never overwritten, the carver extracts 100% of the deleted Aadhaar PDFs and bank credentials. This is why ₹50,000 Crore of IT assets are hoarded in India due to data theft fear."* |
| **Step 4: SIH Solution** | Click **"Execute Secure Wipe"** | *"Our solution implements NIST SP 800-88 Rev 1 standards. It overwrites physical sectors with binary zeroes, purges hidden HPA/DCO sectors, verifies 0.00 entropy, and generates a digitally signed, tamper-proof audit certificate (in PDF and JSON format) to enable verifiable trust and recycling!"* |

---

## ⚙️ Core Technical Concepts Covered in Demo

1. **Logical vs Physical Deletion**:
   - **Logical Deletion (Standard OS)**: Modifies metadata table (MFT/FAT/Inode); leaves payload data untouched.
   - **Physical Sanitization (SIH Tool)**: Overwrites storage blocks at the hardware/sector level.
2. **File Carving**:
   - Scanning raw unallocated blocks for known magic headers (e.g., `%PDF-` for PDFs, `PK\x03\x04` for ZIP/XLSX).
3. **NIST SP 800-88 Standards**:
   - **Clear**: Logical overwrite of all user-accessible storage locations.
   - **Purge**: Executing firmware-level Secure Erase / Cryptographic Key destruction (vital for SSD wear-leveling).
4. **Tamper-Proof Verification**:
   - Generating SHA-256 digital signatures on wipe logs so third-party e-waste auditors can verify device cleanliness before recycling.

---

*Developed for Smart India Hackathon 2025 | Ministry of Mines / JNARDDC*
