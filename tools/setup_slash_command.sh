#!/bin/bash
# Setup script for /obsidian slash command in Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACTOR_SCRIPT="$SCRIPT_DIR/obsidian_extract.py"
WRAPPER_SCRIPT="/usr/local/bin/obsidian-extract"

# Check if Python script exists
if [ ! -f "$EXTRACTOR_SCRIPT" ]; then
    echo "❌ obsidian_extract.py not found at $EXTRACTOR_SCRIPT"
    exit 1
fi

# Make Python script executable
chmod +x "$EXTRACTOR_SCRIPT"

# Create wrapper script with shebang
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# Claude Code Obsidian Integration Wrapper
exec python3 "$(dirname "$0")/../ai-agent-experiment/tools/obsidian_extract.py" "$@"
EOF

# Make wrapper executable
chmod +x "$WRAPPER_SCRIPT"

echo "✅ Setup complete!"
echo ""
echo "📋 Usage in Claude Code:"
echo ""
echo "  /obsidian extract --log-file <path>"
echo "  /obsidian export <vault_path>"
echo "  /obsidian search <query>"
echo "  /obsidian review"
echo "  /obsidian mark <card_id> [--approved|--rejected] [--notes '...']"
echo ""
echo "📖 Examples:"
echo ""
echo "  Extract from Claude Code output:"
echo "    /obsidian extract --text 'claude code output here'"
echo ""
echo "  Export to Obsidian vault:"
echo "    /obsidian export ~/Obsidian/MyVault"
echo ""
echo "  Search knowledge cards:"
echo "    /obsidian search 'Python best practices'"
echo ""
echo "  Monthly review check:"
echo "    /obsidian review"
echo ""
echo "  Mark card as reviewed:"
echo "    /obsidian mark abc123def --approved --notes 'Verified and accurate'"
echo ""
