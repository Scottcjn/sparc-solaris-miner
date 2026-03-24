# Contributing to RustChain SPARC Solaris Miner

Thank you for your interest in contributing to the RustChain SPARC Solaris Miner! This project enables mining RTC tokens on vintage Sun workstations running Solaris. Your contributions help keep retro computing alive and productive.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Architecture-Specific Guidelines](#architecture-specific-guidelines)
- [Solaris Compatibility](#solaris-compatibility)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that expects all participants to:
- Be respectful and inclusive
- Welcome newcomers to retro computing
- Share knowledge about SPARC/Solaris systems
- Help preserve computing history

## Getting Started

### Prerequisites

To contribute effectively, you'll need:

**Physical Hardware (Preferred):**
- Sun Ultra 5, Ultra 10, Ultra 60, or compatible SPARC system
- Solaris 10 installed (Update 8 or later recommended)
- Network connectivity
- 256MB+ RAM

**Emulated Environment (Alternative):**
- QEMU with SPARC support
- Solaris 10 ISO
- Modern host with sufficient resources

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** to your Solaris workstation:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sparc-solaris-miner.git
   cd sparc-solaris-miner
   ```
3. **Test the miner** to ensure it works on your system:
   ```bash
   python rustchain_sparc_miner.py --dry-run
   ```

## Development Environment

### On Physical Sun Hardware

```bash
# Check your system details
prtconf | head -20
psrinfo -v
cat /etc/release

# Verify Python
python --version

# Check network connectivity
ping 50.28.86.131
```

### Using QEMU (Development Alternative)

If you don't have physical SPARC hardware:

```bash
# Create QEMU disk image
qemu-img create -f qcow2 solaris10.qcow2 20G

# Boot Solaris 10 ISO
qemu-system-sparc -m 512 -cdrom sol-10-u11-ga-sparc-dvd.iso \
  -hda solaris10.qcow2 -boot d

# Install git (if not present)
pkgutil -i git
```

### OpenCSW Packages

Many development tools are available through OpenCSW:

```bash
# Update catalog
pkgutil -U

# Useful packages for development
pkgutil -i git
pkgutil -i curl
pkgutil -i vim
pkgutil -i python27
```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

1. **System Information:**
   ```bash
   prtconf | grep -E "(Memory|CPU)"
   psrinfo -v
   cat /etc/release
   uname -a
   ```

2. **Python Version:**
   ```bash
   python --version
   ```

3. **Error Output:** Full traceback or error message

4. **Steps to Reproduce:** Clear steps to recreate the issue

5. **Expected vs Actual Behavior:** What you expected vs what happened

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
- Check existing issues first
- Describe the use case (e.g., "Support for Sun Blade 1500")
- Explain the benefit to retro computing community
- Consider implementation complexity for Solaris 10

### Contributing Code

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test on SPARC hardware** or QEMU when possible

4. **Commit with clear messages:**
   ```bash
   git commit -m "feat: Add support for Sun Blade 1500 detection"
   ```

5. **Push and create a Pull Request**

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines where applicable
- Keep compatibility with Python 2.6+ (Solaris 10 default)
- Use 4 spaces for indentation
- Maximum line length: 100 characters

### Python 2/3 Compatibility

Since Solaris 10 ships with Python 2.6, maintain compatibility:

```python
# Use compatible print
from __future__ import print_function

# Handle string types
try:
    string_types = basestring
except NameError:
    string_types = str

# Safe imports
try:
    import json
except ImportError:
    import simplejson as json
```

### SPARC-Specific Considerations

```python
# Detect architecture properly
def get_sparc_arch():
    """Detect SPARC architecture variant."""
    try:
        output = subprocess.check_output(['psrinfo', '-pv'])
        if 'UltraSPARC-III' in output:
            return 'ultrasparc3'
        elif 'UltraSPARC-II' in output:
            return 'ultrasparc2'
        elif 'UltraSPARC' in output:
            return 'ultrasparc'
        return 'sparc'
    except:
        return 'unknown'
```

### Documentation

- Comment SPARC-specific code sections
- Document Solaris version requirements
- Include hardware compatibility notes

## Testing Guidelines

### Testing on Physical Hardware

When possible, test on actual SPARC systems:

```bash
# Dry run test
python rustchain_sparc_miner.py --dry-run

# Test with verbose output
python rustchain_sparc_miner.py --dry-run --verbose

# Test architecture detection
python -c "import rustchain_sparc_miner; print(rustchain_sparc_miner.detect_arch())"
```

### Testing in QEMU

```bash
# Start QEMU SPARC emulation
qemu-system-sparc -m 512 -hda solaris10.qcow2 -nographic

# Run tests
python rustchain_sparc_miner.py --dry-run
```

### Test Checklist

Before submitting:
- [ ] Code runs on Python 2.6 (Solaris 10 default)
- [ ] Code runs on Python 2.7 (if available)
- [ ] Dry-run mode works without errors
- [ ] Architecture detection works correctly
- [ ] Network connectivity check passes
- [ ] No regression in existing functionality

## Submitting Changes

### Pull Request Process

1. **Update documentation** if needed (README, this file, etc.)

2. **Add to SOLARIS_VERSIONS.md** if adding new system support:
   ```markdown
   | Sun Blade 1500 | UltraSPARC IIIi | Solaris 10 | 1.5x | Your Name |
   ```

3. **Test on your hardware** and report results in PR description

4. **Fill out the PR template:**
   - Description of changes
   - Hardware tested on
   - Solaris version
   - Test results

5. **Request review** from maintainers

### Commit Message Format

Follow conventional commits:

```
feat: Add support for Sun Fire V240
docs: Update Solaris 10 installation guide
fix: Correct CPU frequency detection on UltraSPARC IIIi
perf: Optimize hash calculation for SPARC V9
test: Add QEMU testing instructions
```

## Architecture-Specific Guidelines

### UltraSPARC II/IIi

- Default target architecture
- 64-bit mode supported
- 1.6x antiquity bonus

### UltraSPARC III/IIIi

- Newer systems (Sun Blade 1000/2000)
- Improved cache architecture
- May need specific handling

### SPARC64 (Fujitsu)

- Enterprise servers
- Different CPU detection path
- Test thoroughly if adding support

### Adding New Architecture Support

1. Update `detect_arch()` function
2. Add antiquity bonus calculation
3. Test on actual hardware
4. Document in SOLARIS_VERSIONS.md
5. Update supported systems table in README

## Solaris Compatibility

### Solaris 10 Specifics

- Default Python: 2.6
- Bundled OpenSSL: 0.9.7 (very old)
- Recommended: Use OpenCSW for modern tools

### TLS/SSL Considerations

Solaris 10's OpenSSL is outdated. Options:

1. **Use OpenCSW curl:**
   ```bash
   /opt/csw/bin/curl https://node.rustchain.io
   ```

2. **Use TLS bridge:**
   ```bash
   python rustchain_sparc_miner.py --proxy http://modern-host:8888
   ```

3. **Document workarounds** when contributing TLS-related code

### Package Management

When suggesting new dependencies:
- Prefer OpenCSW packages
- Document installation steps
- Consider Solaris 10