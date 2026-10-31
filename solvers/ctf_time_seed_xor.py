"""
Google CTF — Time-Seeded PRNG XOR Solver
================================================
Challenge: flag XOR-encrypted using:
    random.seed(int(time.time()))
    key = bytes([random.randint(0, 255) for _ in range(L)])

Attack:
  Because the seed is a Unix timestamp (known to within a few minutes),
  brute-force a +/- 3600s window around the approximate timestamp. For
  each candidate seed, regenerate the key and XOR the ciphertext; the
  correct seed yields the printable flag header (HQX{ / flag{ / CTF{).
"""
import random
import re

# ================== CONFIG (update with your real data) ==================
APPROX_TIMESTAMP = 1700000000          # approx. int(time.time())
WINDOW = 3600                           # search +/- this many seconds

CIPHERTEXT_HEX = (
    "00000000000000000000000000000000"   # <-- PASTE YOUR 16-byte hex ciphertext
)
# ========================================================================

ctext = bytes.fromhex(CIPHERTEXT_HEX)
L = len(ctext)

print(f"[*] CTE