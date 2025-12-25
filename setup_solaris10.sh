#!/bin/sh
#
# RustChain Miner Setup for Solaris 10 SPARC
# Run as root
#

echo "================================================"
echo "  RustChain SPARC Miner Setup - Solaris 10"
echo "================================================"
echo ""

# Check we're on Solaris
if [ ! -f /etc/release ]; then
    echo "ERROR: Not running on Solaris"
    exit 1
fi

echo "System: $(head -1 /etc/release)"
echo "Architecture: $(uname -p)"
echo ""

# Check for root
if [ "$(id -u)" != "0" ]; then
    echo "ERROR: Must run as root"
    exit 1
fi

# Step 1: Install OpenCSW
echo "[1/5] Installing OpenCSW package manager..."
if [ ! -x /opt/csw/bin/pkgutil ]; then
    pkgadd -d http://get.opencsw.org/now
else
    echo "  OpenCSW already installed"
fi

# Step 2: Update catalog
echo ""
echo "[2/5] Updating package catalog..."
/opt/csw/bin/pkgutil -U

# Step 3: Install dependencies
echo ""
echo "[3/5] Installing Python and networking tools..."
/opt/csw/bin/pkgutil -y -i python27 curl wget openssl

# Step 4: Download miner
echo ""
echo "[4/5] Downloading RustChain miner..."
cd /opt
mkdir -p rustchain
cd rustchain

/opt/csw/bin/curl -k -O https://raw.githubusercontent.com/Scottcjn/sparc-solaris-miner/main/rustchain_sparc_miner.py
chmod +x rustchain_sparc_miner.py

# Step 5: Create wrapper script
echo ""
echo "[5/5] Creating launcher script..."
cat > /opt/rustchain/start_miner.sh << 'EOF'
#!/bin/sh
# RustChain SPARC Miner Launcher
cd /opt/rustchain
/opt/csw/bin/python2.7 rustchain_sparc_miner.py "$@"
EOF
chmod +x /opt/rustchain/start_miner.sh

# Add to path
echo ""
echo "Adding /opt/csw/bin to system PATH..."
if ! grep -q "/opt/csw/bin" /etc/profile; then
    echo 'PATH=/opt/csw/bin:$PATH; export PATH' >> /etc/profile
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "To start mining:"
echo "  /opt/rustchain/start_miner.sh --wallet YOUR_WALLET_NAME"
echo ""
echo "Options:"
echo "  --wallet NAME    Your miner wallet name (required)"
echo "  --use-http       Use HTTP instead of HTTPS"
echo "  --proxy URL      Use TLS proxy for HTTPS"
echo "  --dry-run        Test without submitting"
echo "  --once           Attest once and exit"
echo ""
echo "Example:"
echo "  /opt/rustchain/start_miner.sh --wallet ultra5-scott"
echo ""
