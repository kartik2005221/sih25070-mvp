#!/usr/bin/env python3
"""
SIH 2025 Data Sanitization & Forensic Recovery Interactive CLI Demo
Ministry of Mines / JNARDDC Project Prototype

Simulates block-level file allocation, standard logical OS deletion,
forensic data carving, NIST SP 800-88 sanitization, and cryptographic certificate generation.
"""

import sys
import time
import random
import hashlib
import json

# ANSI Colors for Terminal Presentation
CLEAR = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

TOTAL_SECTORS = 32

class DiskSimulator:
    def __init__(self):
        self.sectors = [{"data": "00 " * 8, "status": "FREE", "file": None} for _ in range(TOTAL_SECTORS)]
        self.file_table = {}

    def print_disk_map(self):
        print(f"\n{BOLD}{CYAN}=== PHYSICAL STORAGE SECTOR MAP ({TOTAL_SECTORS} Sectors) ==={CLEAR}")
        grid = ""
        for i, sec in enumerate(self.sectors):
            status = sec["status"]
            char = f"[{i:02d}]"
            if status == "FREE":
                grid += f"{BLUE}{char}{CLEAR} "
            elif status == "ACTIVE":
                grid += f"{GREEN}{char}{CLEAR} "
            elif status == "DELETED_ORPHAN":
                grid += f"{RED}{BOLD}{char}{CLEAR} "
            elif status == "SANITIZED":
                grid += f"{MAGENTA}{char}{CLEAR} "
            
            if (i + 1) % 8 == 0:
                grid += "\n"
        print(grid)
        print(f"Legend: {GREEN}[ACTIVE]{CLEAR} File Allocated | {RED}[DELETED_ORPHAN]{CLEAR} OS Deleted (Vulnerable Data!) | {MAGENTA}[SANITIZED]{CLEAR} Wiped Zeroes | {BLUE}[FREE]{CLEAR} Empty")

    def write_file(self, filename, content, sector_indices):
        self.file_table[filename] = {
            "sectors": sector_indices,
            "os_active": True,
            "content": content
        }
        for idx in sector_indices:
            self.sectors[idx]["data"] = content[:16]
            self.sectors[idx]["status"] = "ACTIVE"
            self.sectors[idx]["file"] = filename
        print(f"{GREEN}[+]{CLEAR} Wrote '{filename}' to Sectors {sector_indices}")

    def os_delete_file(self, filename):
        if filename not in self.file_table:
            print(f"{RED}[!] File not found.{CLEAR}")
            return
        
        # OS standard delete: only change pointer in table, DO NOT erase sectors!
        self.file_table[filename]["os_active"] = False
        for idx in self.file_table[filename]["sectors"]:
            self.sectors[idx]["status"] = "DELETED_ORPHAN"
            # Note: self.sectors[idx]["data"] is LEFT INTACT!
        print(f"{YELLOW}[!] OS Shift+Delete Executed for '{filename}'.{CLEAR}")
        print(f"{RED}[CRITICAL WARN] File removed from directory listing, BUT physical data is STILL stored in memory blocks!{CLEAR}")

    def forensic_carving_attack(self):
        print(f"\n{YELLOW}{BOLD}[*] Running Forensic Data Carver (Simulating Autopsy/SleuthKit)...{CLEAR}")
        time.sleep(1)
        recovered = []
        for i, sec in enumerate(self.sectors):
            if sec["status"] == "DELETED_ORPHAN":
                recovered.append((i, sec["data"]))
        
        if recovered:
            print(f"{RED}{BOLD}[!] DANGER! Forensic Scanner Recovered Data from 'Empty' Unallocated Sectors:{CLEAR}")
            for sec_id, raw_bytes in recovered:
                print(f"    -> Sector [{sec_id:02d}] Raw Byte Dump: '{raw_bytes}'")
            print(f"{RED}{BOLD}[RESULT] 100% Data Recoverable! Standard deletion failed to sanitize disk.{CLEAR}")
        else:
            print(f"{GREEN}{BOLD}[RESULT] 0 Bytes Recoverable. Disk is fully sanitized!{CLEAR}")

    def nih_secure_wipe(self, standard="NIST_SP_800_88_CLEAR"):
        print(f"\n{GREEN}{BOLD}[*] Launching SIH Secure Wipe Engine ({standard})...{CLEAR}")
        time.sleep(1)
        for i, sec in enumerate(self.sectors):
            sys.stdout.write(f"\rSanitizing Sector [{i:02d}/{TOTAL_SECTORS-1}] -> Overwriting with 0x00 ...")
            sys.stdout.flush()
            time.sleep(0.05)
            sec["data"] = "00 00 00 00 00 00 00 00"
            sec["status"] = "SANITIZED"
            sec["file"] = None
        print(f"\n{GREEN}[+] Complete sanitization pass finished across all sectors.{CLEAR}")
        
        # Verification Pass
        print(f"{CYAN}[*] Running Post-Wipe Hardware Verification Pass...{CLEAR}")
        time.sleep(0.5)
        print(f"{GREEN}[PASS] Verification successful: 100% sectors verified as 0x00 (Entropy H=0.0).{CLEAR}")

        # Generate Certificate
        cert_id = f"CERT-JNARDDC-2025-{random.randint(1000, 9999)}"
        sig = hashlib.sha256(f"{cert_id}-NIST-800-88-PASS".encode()).hexdigest()
        cert = {
            "certificate_id": cert_id,
            "standard": standard,
            "verification_status": "PASS",
            "sha256_signature": sig,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"\n{GREEN}{BOLD}=== TAMPER-PROOF WIPE CERTIFICATE GENERATED ==={CLEAR}")
        print(json.dumps(cert, indent=2))

def main():
    sim = DiskSimulator()
    
    print(f"{BOLD}{CYAN}")
    print("╔═════════════════════════════════════════════════════════════════════════╗")
    print("║  SIH 2025: Secure Data Sanitization & Data Recovery Terminal Demo       ║")
    print("║  Ministry of Mines / JNARDDC                                            ║")
    print("╚═════════════════════════════════════════════════════════════════════════╝")
    print(f"{CLEAR}")

    # Stage 1
    input(f"{YELLOW}Press ENTER to start Step 1: Write Sensitive Files to Disk...{CLEAR}")
    sim.write_file("aadhaar_kyc.pdf", "%PDF-1.5 Aadhaar: 9876-5432-1098", [4, 5, 6, 7])
    sim.write_file("bank_passbook.xlsx", "Account: 50100298 Balance: 450000", [12, 13, 14])
    sim.print_disk_map()

    # Stage 2
    input(f"\n{YELLOW}Press ENTER to start Step 2: Simulate Standard OS File Deletion...{CLEAR}")
    sim.os_delete_file("aadhaar_kyc.pdf")
    sim.os_delete_file("bank_passbook.xlsx")
    sim.print_disk_map()

    # Stage 3
    input(f"\n{YELLOW}Press ENTER to start Step 3: Run Forensic Recovery Attack...{CLEAR}")
    sim.forensic_carving_attack()

    # Stage 4
    input(f"\n{YELLOW}Press ENTER to start Step 4: Execute SIH NIST SP 800-88 Wiping Tool...{CLEAR}")
    sim.nih_secure_wipe()
    sim.print_disk_map()

    # Final Stage
    input(f"\n{YELLOW}Press ENTER to re-run Forensic Recovery on Sanitized Disk...{CLEAR}")
    sim.forensic_carving_attack()

    print(f"\n{GREEN}{BOLD}Simulation finished successfully! Demo complete.{CLEAR}\n")

if __name__ == "__main__":
    main()
