# Solaris Version Guide for RustChain Mining

## Recommended: Solaris 10

**Why Solaris 10:**
- Last version supporting sun4u (UltraSPARC I/II/III)
- OpenCSW package repository available
- ZFS support (optional but nice)
- Python 2.6 included
- Better networking stack

Download: Oracle Solaris 10 Archive (requires Oracle account)
- sol-10-u11-ga-sparc-dvd.iso (4.4GB)

## Solaris 8 (2.8)

**Can it mine?** Yes, with limitations:
- Python 2.4 max (need to compile 2.6+)
- No modern TLS (use HTTP proxy)
- Smaller package ecosystem
- Original factory install for Ultra 5/10

If you have the original Solaris 8 CD that came with your Ultra 5, that's historically cool! But Solaris 10 is recommended for mining.

**Solaris 8 Python setup:**
```bash
# Compile Python 2.6 from source
gunzip Python-2.6.9.tar.gz
tar xf Python-2.6.9.tar
cd Python-2.6.9
./configure --prefix=/opt/python26
make
make install
```

## Solaris 9

Middle ground - works but Solaris 10 is still better for package availability.

## Version Detection

```bash
# Check your Solaris version
cat /etc/release

# Example outputs:
# Solaris 8 2/02 s28s_u7wos_08a SPARC
# Solaris 10 10/09 s10s_u8wos_08a SPARC
```

## TLS by Solaris Version

| Version | OpenSSL | TLS Max | Mining Mode |
|---------|---------|---------|-------------|
| Solaris 8 | 0.9.6 | SSL3 | HTTP proxy required |
| Solaris 9 | 0.9.7 | TLS 1.0 | HTTP proxy recommended |
| Solaris 10 | 0.9.8 | TLS 1.0 | OpenCSW curl for TLS 1.2 |
| Solaris 11 | 1.0.x | TLS 1.2 | Direct HTTPS works |

## My Recommendation

1. **Install Solaris 10** - Boot from ISO, install to disk
2. **Configure networking** - Static IP recommended
3. **Install OpenCSW** - `pkgadd -d http://get.opencsw.org/now`
4. **Install modern tools** - `pkgutil -i python27 curl wget`
5. **Run miner** - `python rustchain_sparc_miner.py --wallet your-wallet`

Keep that Solaris 8 CD though - it's part of the system's history!

## OpenCSW Quick Setup (Solaris 10)

```bash
# As root
pkgadd -d http://get.opencsw.org/now

# Update catalog
/opt/csw/bin/pkgutil -U

# Install essentials
/opt/csw/bin/pkgutil -i python27 curl wget openssl

# Add to PATH
echo 'export PATH=/opt/csw/bin:$PATH' >> ~/.profile
```

## Solaris 10 Download Links

Official Oracle Archive (registration required):
- https://www.oracle.com/solaris/solaris10/downloads/solaris10-get-jsp-downloads.html

Community mirrors (check legality in your jurisdiction):
- Archive.org sometimes has ISOs
- Sun Freeware archives
