# Contributing to RustChain SPARC Solaris Miner

Thank you for contributing to the RustChain SPARC Solaris miner! This project brings Proof-of-Antiquity mining to vintage Sun workstations.

## Getting Started

### Prerequisites

- Solaris 10 (Update 8 or later recommended)
- Python 2.6+ (included in Solaris 10)
- Network connectivity to a RustChain node
- 256MB+ RAM

### Setup

```bash
# Clone the repository
git clone https://github.com/Scottcjn/sparc-solaris-miner.git
cd sparc-solaris-miner

# Or download the miner directly
curl -O https://raw.githubusercontent.com/Scottcjn/sparc-solaris-miner/main/rustchain_sparc_miner.py

# Run the miner
python rustchain_sparc_miner.py --wallet your-wallet-name
```

### Verifying Your SPARC System

```bash
# Check CPU info
prtconf | head -20
psrinfo -v

# Solaris version
cat /etc/release

# Check Python
python --version

# Test connectivity to RustChain node
ping 50.28.86.131
```

## Making Changes

1. **Fork** the repository
2. **Create a branch** for your change: `git checkout -b fix-broken-link`
3. **Make your change** — keep changes focused and minimal
4. **Test locally** — run `python rustchain_sparc_miner.py --help` to verify syntax
5. **Submit a PR** with a link to this issue

## What Counts

- Fixing a genuinely broken link in README.md or SOLARIS_VERSIONS.md
- Correcting an incorrect command or URL
- Improving clarity of setup instructions
- Adding missing supported hardware

## Anti-Goals (What We Will Not Accept)

- Manufactured whitespace or formatting changes
- Changes that add no real value to documentation
- Changes that break existing instructions

## RustChain Proof-of-Antiquity

This miner earns the **1.6x antiquity bonus** for UltraSPARC II/IIi hardware. When submitting mining-related improvements, keep the Proof-of-Antiquity philosophy in mind: older, verifiable hardware is rewarded more generously.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
