# Contributing to RustChain SPARC Miner

Welcome! This project enables RTC mining on vintage Sun SPARC workstations.

## Development Setup

```bash
# Clone your fork
git clone https://github.com/MingYu5/sparc-solaris-miner.git
cd sparc-solaris-miner

# Test miner
python rustchain_sparc_miner.py --wallet YOUR_WALLET
```

## Supported Hardware

- Ultra 5/10/60 (UltraSPARC IIi/II)
- Sun Blade 100/150 (UltraSPARC IIe)
- Sun Fire V100
- Enterprise 250/450

## Code Style

- Python 2.6+ compatible (Solaris 10 ships with Python 2.6)
- 4 spaces indentation
- Avoid modern Python features (f-strings, type hints require 3.6+)

## Pull Request Process

1. Fork the repo
2. Create a feature branch
3. Test on real SPARC hardware (VMs will be penalized)
4. Open PR against `Scottcjn/sparc-solaris-miner:main`

## Testing

```bash
# Dry run
python rustchain_sparc_miner.py --wallet test --dry-run

# Check hardware detection
python -c "import platform; print(platform.uname())"
```

## Notes

- This is a legacy project targeting vintage hardware
- Ensure compatibility with Solaris 10 Python 2.6+
- Network tests should work with both modern TLS and legacy protocols

Questions? Open an issue!
