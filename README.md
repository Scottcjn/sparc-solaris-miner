[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![SPARC](https://img.shields.io/badge/SPARC-Solaris-yellow)](https://github.com/Scottcjn/sparc-solaris-miner) [![UltraSPARC](https://img.shields.io/badge/UltraSPARC-1.6x-green)](https://github.com/Scottcjn/sparc-solaris-miner)

# RustChain SPARC Miner for Solaris

**Mine RTC on your vintage Sun workstation** - UltraSPARC gets 1.6x antiquity bonus!

## Supported Hardware

| System | CPU | Solaris Version | Antiquity Bonus |
|--------|-----|-----------------|-----------------|
| Ultra 5 | UltraSPARC IIi 270-400MHz | Solaris 10 | 1.6x |
| Ultra 10 | UltraSPARC IIi 300-440MHz | Solaris 10 | 1.6x |
| Ultra 60 | UltraSPARC II 300-450MHz | Solaris 10 | 1.6x |
| Sun Blade 100/150 | UltraSPARC IIe 500-650MHz | Solaris 10 | 1.5x |
| Sun Fire V100 | UltraSPARC IIi 550-650MHz | Solaris 10 | 1.5x |
| Enterprise 250/450 | UltraSPARC II | Solaris 10 | 1.6x |

## Requirements

- Solaris 10 (Update 8 or later recommended)
- Python 2.6+ (included in Solaris 10)
- Network connectivity to RustChain node
- 256MB+ RAM

## Quick Start

```bash
# Download miner
curl -O https://raw.githubusercontent.com/Scottcjn/sparc-solaris-miner/main/rustchain_sparc_miner.py

# Or use wget
wget https://raw.githubusercontent.com/Scottcjn/sparc-solaris-miner/main/rustchain_sparc_miner.py

# Run miner
python rustchain_sparc_miner.py --wallet your-wallet-name
```

## Solaris 10 Setup

### Check Your System
```bash
# CPU info
prtconf | head -20
psrinfo -v

# Solaris version
cat /etc/release

# Check Python
python --version
```

### Install Dependencies (if needed)
```bash
# Update OpenCSW catalog (if using OpenCSW)
pkgutil -U

# Install Python 2.7 (if not present)
pkgutil -i python27

# Install curl with modern TLS
pkgutil -i curl
```

### Network Configuration
```bash
# Check network
ifconfig -a
netstat -rn

# Test connectivity to RustChain node
ping 50.28.86.131

# Test HTTP (Solaris curl may be old)
/opt/csw/bin/curl -k https://50.28.86.131/health
```

## TLS Considerations

Solaris 10's bundled OpenSSL is ancient (0.9.7). Options:

1. **OpenCSW curl** - Install modern curl via OpenCSW
2. **TLS Bridge** - Use HTTP proxy on your network
3. **HTTP mode** - Use `--use-http` flag (less secure)

### Using TLS Bridge
If you have a modern machine on your network running the TLS bridge:
```bash
python rustchain_sparc_miner.py --wallet my-ultra5 --proxy http://192.168.0.160:8888
```

## SPARC Architecture Detection

The miner automatically detects:
- CPU type (UltraSPARC I/II/III/IV, SPARC64)
- Clock speed
- Number of CPUs/cores
- L2 cache size

This determines your antiquity multiplier for RTC rewards.

## Fingerprint Checks

SPARC-specific hardware fingerprinting:
- `/usr/sbin/prtconf` output hash
- `/usr/sbin/psrinfo` timing patterns
- Memory controller latency
- OpenBoot PROM version

VMs (QEMU sparc64, zones) are detected and receive minimal rewards.

## Troubleshooting

### "SSL handshake failed"
```bash
# Use HTTP proxy mode
python rustchain_sparc_miner.py --wallet x --use-http

# Or use TLS bridge
python rustchain_sparc_miner.py --wallet x --proxy http://proxy:8888
```

### "Python version too old"
```bash
# Install Python 2.7 via OpenCSW
pkgutil -i python27
/opt/csw/bin/python2.7 rustchain_sparc_miner.py --wallet x
```

### "Connection refused"
```bash
# Check firewall rules
svcs -a | grep ipfilter
svcadm disable ipfilter  # Temporarily disable

# Check routing
netstat -rn
route add default 192.168.0.1  # Set gateway
```

## Building from Source

For maximum compatibility, you can build Python 3 on Solaris 10:

```bash
# Get build tools
pkgutil -i gcc5core gmake

# Download Python source
curl -O https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tar.xz

# Build
gtar xf Python-3.8.18.tar.xz
cd Python-3.8.18
./configure --prefix=/opt/python38
gmake -j2
sudo gmake install
```

## Why SPARC?

The UltraSPARC was the workstation CPU of the 90s:
- First 64-bit commercial microprocessor (1995)
- SPARC V9 architecture - clean, elegant RISC
- VIS (Visual Instruction Set) - early SIMD
- Sun's golden era before Oracle

RustChain rewards vintage hardware because:
1. **Real silicon** - No VMs, no emulation
2. **Historical significance** - Computing heritage
3. **Anti-farm** - Can't spin up 1000 UltraSPARCs on AWS

## Community

- GitHub Issues: Report problems
- RustChain Discord: #vintage-mining channel
- Elyan Labs: https://elyanlabs.com

## License

MIT - Use freely, mine responsibly.

---

*Built Christmas 2025 - The Sun never sets on SPARC mining*
