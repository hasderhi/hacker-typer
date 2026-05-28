#!/usr/bin/env python3

import tty
import sys
import termios
import os
import re

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

fake_output = [
    "[+] Initializing remote session handler...",
    "[+] Loading encrypted runtime modules (AES-256-GCM)...",
    "[+] Verifying secure tunnel integrity... OK",
    "[+] Establishing relay chain:",
    "    -> node-eu-01.frankfurt (latency: 12ms)",
    "    -> node-se-04.stockholm (latency: 24ms)",
    "    -> node-us-09.chicago (latency: 98ms)",
    "    -> exit-relay masked (IP: 104.26.3.12)",
    "[+] Tunnel obfuscation: ChaCha20-Poly1305",
    "",

    "$ uname -a",
    "Linux archforge 6.12.7-arch1-1 x86_64 GNU/Linux",
    "",
    "$ cat /etc/os-release",
    "NAME=Arch Linux",
    "PRETTY_NAME=\"Arch Linux\"",
    "ID=arch",
    "ID_LIKE=archlinux",
    "",
    "$ whoami && id",
    "root",
    "uid=0(root) gid=0(root) groups=0(root)",
    "",
    "$ hostnamectl",
    "   Static hostname: archforge",
    "         Icon name: computer-vm",
    "           Chassis: vm",
    "        Machine ID: a1b2c3d4e5f67890",
    "           Boot ID: x9y8z7w6v5u4t3s2r1q0",
    "    Virtualization: kvm",
    "  Operating System: Arch Linux",
    "            Kernel: Linux 6.12.7-arch1-1",
    "      Architecture: x86-64",
    "",

    "$ ip addr show",
    "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000",
    "    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00",
    "    inet 127.0.0.1/8 scope host lo",
    "       valid_lft forever preferred_lft forever",
    "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000",
    "    link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff",
    "    inet 192.168.1.22/24 brd 192.168.1.255 scope global dynamic eth0",
    "       valid_lft 86399sec preferred_lft 86399sec",
    "    inet6 fe80::211:22ff:fe33:4455/64 scope link",
    "       valid_lft forever preferred_lft forever",
    "",
    "$ ip route",
    "default via 192.168.1.1 dev eth0 proto dhcp metric 100",
    "192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.22 metric 100",
    "",
    "$ ss -tunap",
    "Netid  State   Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process",
    "tcp    ESTAB   0       0       192.168.1.22:4481    45.83.221.17:443    users:((\"stealth-agent\",pid=4021,fd=3))",
    "tcp    ESTAB   0       0       192.168.1.22:22       172.19.44.8:49821   users:((\"sshd\",pid=1234,fd=4))",
    "udp    UNCONN  0       0       0.0.0.0:68           0.0.0.0:*            users:((\"dhcpcd\",pid=567,fd=6))",
    "",

    "$ journalctl -p 3 -xb --no-pager",
    "May 28 02:14:05 archforge kernel: usb 1-2: device descriptor read/64, error -71",
    "May 28 02:14:07 archforge systemd[1]: Failed to start transient stealth-monitor.service: Unit stealth-monitor.service not found.",
    "May 28 02:14:09 archforge sshd[1234]: Accepted publickey for root from 172.19.44.8 port 49821 ssh2: RSA SHA256:AbCdEfGhIjKlMnOpQrStUvWxYz",
    "",

    "[SYS] Kernel privilege escalation module loaded (CVE-2024-1234)",
    "[SYS] Memory region scanner attached to PID 4021 (stealth-agent)",
    "[SYS] Kernel module: rootkit_stealth.ko (hidden from lsmod)",
    "[NET] Passive packet monitor enabled on interface eth0 (libpcap)",
    "[NET] ARP table snapshot complete: 5 entries cached",
    "[NET] DNS cache poisoning routines prepared (target: 8.8.8.8)",
    "",

    "$ nmap -sV -O -T4 192.168.1.0/24",
    "Starting Nmap 7.94 ( https://nmap.org )",
    "Nmap scan report for 192.168.1.1",
    "Host is up (0.0023s latency).",
    "PORT    STATE SERVICE     VERSION",
    "80/tcp  open  http        DD-WRT httpd",
    "443/tcp open  ssl/http    DD-WRT httpd",
    "MAC Address: AA:BB:CC:DD:EE:FF (Unknown)",
    "Device type: WAP|broadband router",
    "Running: Linux 3.X|4.X, DD-WRT v3",
    "OS CPE: cpe:/o:dd-wrt:dd-wrt:3.0 cpe:/h:dd-wrt:dd-wrt",
    "OS details: DD-WRT v3 (Linux 3.10 - 4.9)",
    "",
    "Nmap scan report for 192.168.1.14",
    "Host is up (0.0045s latency).",
    "PORT    STATE SERVICE     VERSION",
    "631/tcp open  ipp         CUPS 2.4",
    "MAC Address: 11:22:33:44:55:66 (Xerox)",
    "Device type: printer",
    "Running: Linux 3.X|4.X",
    "",
    "Nmap scan report for 192.168.1.37",
    "Host is up (0.0012s latency).",
    "PORT    STATE SERVICE     VERSION",
    "139/tcp open  netbios-ssn Samba smbd 4.6.2",
    "445/tcp open  netbios-ssn Samba smbd 4.6.2",
    "MAC Address: 66:55:44:33:22:11 (ASUSTek COMPUTER)",
    "Device type: general purpose",
    "Running: Linux 4.X",
    "OS CPE: cpe:/o:linux:linux_kernel:4.15",
    "OS details: Linux 4.15 - 5.6",
    "VULNERABILITIES:",
    "CVE-2017-7494: EternalBlue (Samba)",
    "",
    "$ sudo tcpdump -i eth0 port 443 -c 5 -nn",
    "tcpdump: verbose output suppressed, use -v or -vv for full protocol decode",
    "listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes",
    "02:14:10.123456 IP 192.168.1.37.54321 > 104.26.3.12.443: Flags [P.], seq 1:513, ack 1, win 512, options [nop,nop,TS val 123456789 ecr 987654321], length 512",
    "02:14:10.123789 IP 192.168.1.22.4481 > 172.67.74.201.443: Flags [S], seq 0, win 64240, options [mss 1460,sackOK,TS val 234567890 ecr 0,nop,wscale 7], length 0",
    "02:14:10.234567 IP 172.67.74.201.443 > 192.168.1.22.4481: Flags [S.], seq 0, ack 1, win 64240, options [mss 1460,sackOK,TS val 345678901 ecr 234567890,nop,wscale 7], length 0",
    "",

    "[DB] Extracting credential artifacts from /etc/shadow...",
    "[DB] Hash dump progress: 42% (ETA: 00:02:15)",
    "[DB] Parsing shadow entries: 7/15 users processed",
    "[DB] Found weak hash: $6$rounds=5000$salt$hash (user: admin)",
    "[AUTH] Attempting token impersonation for user: admin...",
    "[AUTH] Token generated: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE3MTk2ODUyMDB9.abc123def456ghi789",
    "",

    "$ cat /etc/passwd",
    "root:x:0:0:root:/root:/bin/bash",
    "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
    "bin:x:2:2:bin:/bin:/usr/sbin/nologin",
    "sys:x:3:3:sys:/dev:/usr/sbin/nologin",
    "admin:x:1000:1000:Admin User:/home/admin:/bin/bash",
    "",
    "$ grep -R --include='*.pem' --include='*.key' 'PRIVATE KEY' /home 2>/dev/null",
    "/home/admin/.ssh/id_rsa",
    "/home/admin/.config/burp/proxy_ca.pem",
    "",
    "$ ls -la /home/admin/.ssh/",
    "total 24",
    "-rw------- 1 admin admin 2610 May 28 02:10 id_rsa",
    "-rw-r--r-- 1 admin admin  577 May 28 02:10 id_rsa.pub",
    "-rw-r--r-- 1 admin admin  412 May 28 02:10 known_hosts",
    "",

    "function deriveKey(sessionEntropy, hostSeed):",
    "    salt = hashlib.sha256(sessionEntropy + hostSeed).digest()",
    "    return hashlib.pbkdf2_hmac('sha512', b'static_secret', salt, 100000)",
    "",
    "function decryptPayload(blob):",
    "    key = deriveKey(sessionEntropy, hostSeed)",
    "    cipher = AES.new(key, AES.MODE_GCM, nonce=blob[:12])",
    "    return cipher.decrypt(blob[12:])",
    "",
    "class RelayNode:",
    "    def __init__(self, ip, port, latency):",
    "        self.ip = ip",
    "        self.port = port",
    "        self.latency = latency",
    "        self.status = 'active'",
    "    ",
    "    def rotateIdentity(self):",
    "        self.ip = generateSpoofedIP()",
    "        self.port = random.randint(1024, 65535)",
    "        log(f'[RELAY] Rotated identity to {self.ip}:{self.port}')",
    "",
    "for target in discovered_hosts:",
    "    fingerprint = scan_os(target)",
    "    if fingerprint.vulnerable:",
    "        exploit = selectExploit(fingerprint.cve)",
    "        if exploit:",
    "            queue_exploit(target, exploit)",
    "            if elevate_privileges(target):",
    "                log(f'[SUCCESS] Root access gained on {target}')",
    "            else:",
    "                log(f'[FAIL] Privilege escalation failed on {target}')",
    "",

    "$ ps aux --sort=-%mem | head -n 6",
    "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND",
    "root      4021  0.0 22.4 123456 78901 ?        Sl   02:10   0:05 stealth-agent --daemon",
    "mysql      911  0.5  4.1 234567 34567 ?        Ssl  02:05   0:12 /usr/bin/mysqld --basedir=/usr",
    "root      5678  0.2  3.2  45678 23456 ?        S    02:12   0:01 python3 /opt/runtime/main.py",
    "nginx     1234  0.1  1.8  98765 12345 ?        S    02:08   0:03 nginx: worker process",
    "root      2345  0.0  0.5  12345  4567 ?        S    02:10   0:00 /usr/sbin/sshd -D",
    "",
    "$ top -bn1 | grep '%Cpu'",
    "%Cpu(s):  5.2 us,  1.8 sy,  0.0 ni, 92.9 id,  0.1 wa,  0.0 hi,  0.0 si,  0.0 st",
    "",

    "$ find / -name '*.log' -mtime -1 -type f 2>/dev/null | head -n 10",
    "/var/log/auth.log",
    "/var/log/pacman.log",
    "/var/log/syslog",
    "/opt/runtime/cache/session.log",
    "/home/admin/.local/share/burp/logs/access.log",
    "/tmp/stealth-agent/debug.log",
    "",
    "$ tail -n 20 /var/log/auth.log",
    "May 28 02:10:01 archforge sshd[1234]: Accepted publickey for root from 172.19.44.8 port 49821 ssh2: RSA SHA256:AbCdEfGhIjKlMnOpQrStUvWxYz",
    "May 28 02:10:05 archforge su[5678]: Successful su for root by admin",
    "May 28 02:12:45 archforge sudo: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow",
    "",

    "[AI] Adaptive heuristic engine started (v2.1.0)",
    "[AI] Behavioral anomaly score: 0.13 (threshold: 0.5)",
    "[AI] Countermeasure bypass confidence: 94.2%",
    "[AI] Predicted next action: privilege escalation (probability: 87%)",
    "",

    ":: NETWORK TOPOLOGY ::",
    "192.168.1.1      gateway        reachable (DD-WRT)",
    "192.168.1.14     printer        ignored (Xerox)",
    "192.168.1.22     workstation    monitored (archforge)",
    "192.168.1.37     media-node     vulnerable (Samba 4.6.2)",
    "192.168.1.51     backup-host    pending (offline)",
    "",

    "$ inject --payload memhook.bin --target 192.168.1.37 --port 445",
    "[>] Uploading payload chunks (1/3)...",
    "[>] Uploading payload chunks (2/3)...",
    "[>] Uploading payload chunks (3/3)...",
    "[>] Verifying execution signature... OK",
    "[+] Remote thread injection successful (TID: 0x7f8a1234)",
    "[+] Payload executed: memhook.bin (PID: 5432)",
    "",

    "if intrusionDetected():",
    "    purgeTempFiles('/tmp/stealth-agent/')",
    "    wipeSessionKeys('/opt/runtime/keys/')",
    "    rerouteTraffic('node-us-09.chicago')",
    "    log('Intrusion detected: countermeasures activated')",
    "",

    "$ openssl s_client -connect 104.26.3.12:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -text | grep -A 2 'Subject:'",
    "        Subject: CN=example.com, O=Example Inc, L=San Francisco, ST=California, C=US",
    "        Start date: May 20 00:00:00 2026 GMT",
    "        End date:   May 20 00:00:00 2027 GMT",
    "",
    "[CRYPTO] Generating ephemeral RSA-4096 session keys...",
    "[CRYPTO] Handshake entropy: 256 bits (sufficient)",
    "[CRYPTO] Secure channel established (TLS 1.3, AES-256-GCM, SHA384)",
    "",

    "$ sudo journalctl -fu sshd --no-pager | tail -n 5",
    "May 28 02:14:05 archforge sshd[1234]: Accepted publickey for root from 172.19.44.8 port 49821 ssh2: RSA SHA256:AbCdEfGhIjKlMnOpQrStUvWxYz",
    "May 28 02:14:07 archforge sshd[1234]: pam_unix(sshd:session): session opened for user root by (uid=0)",
    "May 28 02:14:10 archforge sshd[1234]: Received disconnect from 172.19.44.8 port 49821:11: disconnected by user",
    "",

    "> sudo ./spectre_mapper --deep-scan --silent --output /tmp/spectre.log",
    "[SPECTRE] Scanning memory sectors...",
    "[SPECTRE] Mapping hardware interrupts...",
    "[SPECTRE] Collecting entropy samples... (1024/4096)",
    "[SPECTRE] Detecting hypervisor signatures... (KVM detected)",
    "[SPECTRE] Scan complete. Results saved to /tmp/spectre.log",
    "",

    "THREAD[04] :: listening on port 4481 (stealth-agent)",
    "THREAD[07] :: packet replay initialized (target: 192.168.1.37)",
    "THREAD[11] :: secure wipe daemon active (interval: 300s)",
    "THREAD[15] :: heartbeat monitor (relay chain)",
    "",

    "$ watch -n 1 sensors 2>&1 | head -n 10",
    "Package id 0:  +61.0°C  (high = +80.0°C, crit = +100.0°C)",
    "Core 0:        +58.0°C  (high = +80.0°C, crit = +100.0°C)",
    "Core 1:        +56.0°C  (high = +80.0°C, crit = +100.0°C)",
    "Core 2:        +54.0°C  (high = +80.0°C, crit = +100.0°C)",
    "Core 3:        +52.0°C  (high = +80.0°C, crit = +100.0°C)",
    "",

    "[LOG] 02:14:08 -> relay heartbeat stable (node-eu-01)",
    "[LOG] 02:14:11 -> latency spike detected (node-se-04: 24ms -> 120ms)",
    "[LOG] 02:14:13 -> rerouting through fallback node (node-fi-02.helsinki)",
    "[LOG] 02:14:15 -> tunnel stabilized (latency: 15ms)",
    "",

    "# pseudo runtime output (memory dump)",
    "0x7ffde4a0 :: WRITE  512 bytes (payload: shellcode)",
    "0x7ffde6c0 :: EXEC   shellcode segment (PID: 4021)",
    "0x7ffde810 :: READ   encrypted payload (AES-256-GCM)",
    "0x7ffde990 :: CLEAR  forensic traces (secure wipe)",
    "",

    "for sector in encrypted_volume:",
    "    checksum = calculateChecksum(sector, algorithm='SHA-256')",
    "    if checksum != sector.expected:",
    "        log(f'[WARN] Checksum mismatch in sector {sector.id}')",
    "        rebuildIndex(sector)",
    "        sector.retries += 1",
    "        if sector.retries > 3:",
    "            markSectorAsCorrupt(sector)",
    "",

    "$ rm -rf /tmp/.cache_trace /tmp/stealth-agent/ /opt/runtime/cache/",
    "[CLEANUP] Temporary files purged",
    "",
    "$ shred -zu 10 /opt/runtime/keys/session.key",
    "[CLEANUP] Session keys securely wiped",
    "",

    "[████████████████░░░░░░░░] 78% (Encrypting logs...)",
    "[████████████████████░░░░] 92% (Scrubbing metadata...)",
    "[████████████████████████] 100% (Cleanup complete)",
    "",
    "[FINALIZER] Session cleanup initiated...",
    "[FINALIZER] Volatile memory purge complete",
    "[FINALIZER] Connection terminated safely (exit code: 0)",
    "[FINALIZER] All traces removed. Ready for next operation."
]


orig_settings = termios.tcgetattr(sys.stdin)

tty.setcbreak(sys.stdin)

os.system("clear")

sys.stdout.write("\033]0;Secure Remote Session\a")

index = 0

print(f"{GREEN}{BOLD}Press any key to continue... (ESC to quit){RESET}\n")

def colorize(line):
    """
    Make code/command-looking lines red,
    everything else hacker green.
    Not 100% reliable but, in this case, it doesn't matter...
    """

    code_patterns = [
        r"^\$ ",
        r"^for ",
        r"^\s+",
        r"^function ",
        r"^if ",
        r"^while ",
        r".*\(.*\).*",
        r".*=.*",
    ]

    for pattern in code_patterns:
        if re.match(pattern, line):
            return f"{RED}{line}{RESET}"

    return f"{GREEN}{line}{RESET}"

try:
    while True:
        char = sys.stdin.read(1)

        # ESC quits
        if ord(char) == 27:
            break

        if index >= len(fake_output):
            index = 0
            print(f"{GREEN}\n[REPLAY BUFFER RESET]\n{RESET}")

        print(colorize(fake_output[index]))

        index += 1

finally:
    # Restore settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    print(RESET)