"""
wipe_engine.py

Demo-safe secure erase engine.

IMPORTANT SCOPE NOTE (say this in your pitch):
This performs a REAL multi-pass overwrite-then-delete on files inside a
sandboxed demo folder (demo_target/), not on a raw physical disk/partition.
Raw block-device access (needed for real HPA/DCO handling and SSD sector
remapping) requires OS-level privileges and platform-specific drivers per
NIST SP 800-88 -- that's the "Phase 2" engineering work. This module proves
the erase -> log -> certify -> verify pipeline end-to-end.
"""

import os
import time
from datetime import datetime, timezone

PASSES = 3  # random -> zero -> random, loosely modeled on DoD 5220.22-M style passes


def _overwrite_file(path: str, passes: int = PASSES):
    size = os.path.getsize(path)
    with open(path, "r+b") as f:
        for i in range(passes):
            f.seek(0)
            if i % 2 == 0:
                f.write(os.urandom(size))
            else:
                f.write(b"\x00" * size)
            f.flush()
            os.fsync(f.fileno())
    return size


def wipe_directory(target_dir: str, device_id: str) -> dict:
    """
    Overwrites every file in target_dir `PASSES` times, then deletes it.
    Returns a wipe_result dict ready to be handed to cert_engine.build_certificate_json.
    """
    start_time = datetime.now(timezone.utc).isoformat()
    files_wiped = []
    total_bytes = 0

    for fname in sorted(os.listdir(target_dir)):
        fpath = os.path.join(target_dir, fname)
        if not os.path.isfile(fpath):
            continue
        size = _overwrite_file(fpath, PASSES)
        os.remove(fpath)
        total_bytes += size
        files_wiped.append({
            "name": fname,
            "size_bytes": size,
            "passes": PASSES,
        })
        time.sleep(0.05)  # tiny delay so a live demo can visibly show progress

    end_time = datetime.now(timezone.utc).isoformat()

    return {
        "device_id": device_id,
        "wipe_method": f"NIST SP 800-88 Clear-equivalent -- {PASSES}-pass overwrite "
                        f"(Random / Zero / Random) + delete",
        "files_wiped": files_wiped,
        "total_files": len(files_wiped),
        "total_bytes": total_bytes,
        "start_time": start_time,
        "end_time": end_time,
        "status": "SUCCESS" if files_wiped else "NO_FILES_FOUND",
        "software": "SecureWipe MVP v0.1 (SIH prototype)",
    }
