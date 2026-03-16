# Obsidian × Claude Code Integration Slash Command

Complete implementation guide for the `/obsidian` slash command that extracts knowledge from Claude Code logs and integrates with Obsidian vaults.

## 📋 Quick Start

### Installation

```bash
# 1. Make Python script executable
chmod +x /Users/in/ai-agent-experiment/tools/obsidian_extract.py

# 2. Create symbolic link for easy access
ln -s /Users/in/ai-agent-experiment/tools/obsidian_extract.py /usr/local/bin/obsidian-extract

# 3. Verify installation
obsidian-extract --help
```

### Basic Usage

```bash
# Extract knowledge cards from text with [EXTRACT_AS_KNOWLEDGE] markers
obsidian-extract extract --text "[EXTRACT_AS_KNOWLEDGE]
This is a knowledge card about Python optimization techniques...
[/EXTRACT_AS_KNOWLEDGE]"

# Export all cards to Obsidian vault
obsidian-extract export ~/Obsidian/MyVault

# Search knowledge cards
obsidian-extract search "Python best practices"

# Monthly review check
obsidian-extract review

# Mark card as reviewed
obsidian-extract mark abc123def --approved --notes "Verified and accurate"
```

---

## 🎯 Core Features

### 1. **[EXTRACT_AS_KNOWLEDGE] Marker Detection**

Wrap any content you want to capture as a knowledge card:

```
[EXTRACT_AS_KNOWLEDGE]
# Python List Comprehension Best Practices

List comprehensions are 2-3x faster than loops for most use cases.
Example: [x*2 for x in range(1000)] instead of a for loop.

#python #optimization #best-practices
[/EXTRACT_AS_KNOWLEDGE]
```

**Validation Rules:**
- Minimum 50 characters of content
- Supports inline hashtags for automatic tagging
- Duplicate detection prevents duplicates
- First line becomes the title (up to 100 chars)

### 2. **SQLite Storage with FTS5**

All knowledge cards are stored in SQLite with full-text search indexing:

```
Database: ~/scripts/LLMLogger/knowledge.db

Tables:
├── knowledge_cards
│   ├── id (TEXT PRIMARY KEY)
│   ├── title, content
│   ├── source_log, extracted_at
│   ├── tags (JSON array)
│   ├── reviewed (0/1)
│   └── obsidian_node_id
└── knowledge_fts
    └── (FTS5 virtual table for fast search)
```

### 3. **Obsidian Vault Integration**

Export cards as beautifully formatted markdown notes:

```markdown
---
id: abc123def
node_type: auto-extracted
node_id: auto-abc123def
source: claude-code-log
extracted_at: 2026-03-06T10:30:00
reviewed: false
tags: ["python", "optimization", "best-practices"]
---

# Python List Comprehension Best Practices

## Content
List comprehensions are 2-3x faster than loops...

## Metadata
- **Extracted**: 2026-03-06T10:30:00
- **Source**: claude-code-log
- **Status**: ⏳ Pending Review
- **Tags**: python, optimization, best-practices

## References
*Add backlinks here for Obsidian graph visualization*
```

**Node Types (Visual Distinction):**
- 🟢 `auto-` prefix = Auto-extracted from Claude Code logs
- 🔵 `human-` prefix = Human-reviewed and approved

### 4. **Full-Text Search (FTS5)**

```bash
# Simple search
obsidian-extract search "Python optimization"

# Search with limit
obsidian-extract search "database" --limit 20

# Complex FTS5 queries
obsidian-extract search "python AND (optimization OR performance)"
obsidian-extract search "best-practices" --limit 5
```

Returns:
- Card ID
- Title
- Content preview (first 100 chars)
- Extraction date
- Associated tags

### 5. **Monthly Quality Review**

```bash
# Check accumulated cards needing review
obsidian-extract review

# Output example:
# 📊 Monthly Review Check
#    Unreviewed: 18
#    Accumulated days: 12
#    ⚠️  18 cards pending review
#    Recommendation: REVIEW
```

**Review Workflow (60 minutes/month):**
1. Run `obsidian-extract review` to see statistics
2. Manually review each card in Obsidian
3. Mark approved/rejected using the `mark` command
4. Optionally export only reviewed cards for final vault

---

## 💻 Command Reference

### `extract` - Extract Knowledge Cards

Extract cards from text or log files containing `[EXTRACT_AS_KNOWLEDGE]` markers.

```bash
obsidian-extract extract --text "<text-content>"
obsidian-extract extract --log-file path/to/log.txt
obsidian-extract extract --log-file path/to/log.txt --source "my-session"
```

**Options:**
- `--text, -t` - Direct text input
- `--log-file, -f` - Path to log file
- `--source, -s` - Source identifier (default: `claude-code-log`)
- `--db` - Custom database path

**Output:**
```
✅ Extracted 3 cards, stored 3
   → abc123def
   → def456ghi
   → ghi789jkl
```

### `export` - Export to Obsidian Vault

Export knowledge cards as markdown files to your Obsidian vault.

```bash
obsidian-extract export ~/Obsidian/MyVault
obsidian-extract export ~/Obsidian/MyVault --reviewed-only
```

**Options:**
- `vault_path` - Path to Obsidian vault root directory
- `--reviewed-only` - Export only cards marked as reviewed
- `--db` - Custom database path

**Output:**
```
✅ Exported 12 cards to ~/Obsidian/MyVault/Knowledge Cards
```

**File Structure:**
```
MyVault/
└── Knowledge Cards/
    ├── auto-abc123-Python-List-Comprehension.md
    ├── auto-def456-React-Hooks-Pattern.md
    ├── human-ghi789-Database-Optimization.md
    └── ...
```

### `search` - Full-Text Search

Search knowledge cards using FTS5 full-text search.

```bash
obsidian-extract search "Python optimization"
obsidian-extract search "database" --limit 20
obsidian-extract search "python AND performance"
```

**Options:**
- `query` - Search query (supports FTS5 syntax)
- `--limit, -l` - Maximum results (default: 10)
- `--db` - Custom database path

**Output:**
```
🔍 Found 3 results:

📝 Python List Comprehension Best Practices (abc123)
   List comprehensions are 2-3x faster than loops...

📝 Python Performance Profiling Guide (def456)
   Use cProfile for function-level profiling...

📝 Python Memory Management Tips (ghi789)
   Understand reference counting and garbage collection...
```

### `review` - Monthly Quality Check

Run periodic quality review to flag accumulated unreviewed cards.

```bash
obsidian-extract review
```

**Output:**
```
📊 Monthly Review Check
   Unreviewed: 18
   Accumulated days: 12
   ⚠️  18 cards pending review
   Recommendation: REVIEW
```

**Thresholds:**
- ≤ 10 cards: `MONITOR` (no action needed)
- 11-20 cards: `REVIEW` (60-min review recommended)
- 20+ cards: `⚠️  WARNING` (immediate review needed)

### `mark` - Mark as Reviewed

Mark a knowledge card as approved or rejected after review.

```bash
obsidian-extract mark abc123def --approved
obsidian-extract mark abc123def --approved --notes "Verified and accurate"
obsidian-extract mark abc123def --rejected --notes "Outdated information"
```

**Options:**
- `card_id` - Card ID to mark
- `--approved` - Mark as approved
- `--rejected` - Mark as rejected
- `--notes, -n` - Review notes or comments
- `--vault, -v` - Obsidian vault path (for audit trail)

**Output:**
```
✅ Approved: abc123def
```

---

## 🔧 Advanced Usage

### Integration with Claude Code Hooks

Add to your Claude Code configuration to auto-trigger extraction:

```json
{
  "hooks": {
    "on_command_complete": {
      "condition": "[EXTRACT_AS_KNOWLEDGE] in output",
      "action": "exec obsidian-extract extract --log-file ${CLAUDE_CODE_LOG}"
    }
  }
}
```

### Batch Processing

Extract from multiple log files:

```bash
for log in logs/*.txt; do
  obsidian-extract extract --log-file "$log" --source "batch-$(date +%Y%m%d)"
done
```

### Scheduled Exports (cron)

```bash
# Monthly review (1st of month at 9 AM)
0 9 1 * * obsidian-extract review

# Weekly export to vault (Sunday 11 PM)
0 23 * * 0 obsidian-extract export ~/Obsidian/MyVault --reviewed-only
```

### Custom Database Location

```bash
export KNOWLEDGE_DB=/path/to/custom/knowledge.db
obsidian-extract extract --text "..." --db $KNOWLEDGE_DB
obsidian-extract export ~/Obsidian --db $KNOWLEDGE_DB
```

### Database Inspection

```bash
# List all cards
sqlite3 ~/scripts/LLMLogger/knowledge.db \
  "SELECT id, title, extracted_at FROM knowledge_cards LIMIT 10"

# Find unreviewed cards
sqlite3 ~/scripts/LLMLogger/knowledge.db \
  "SELECT COUNT(*) FROM knowledge_cards WHERE reviewed = 0"

# Search by tag
sqlite3 ~/scripts/LLMLogger/knowledge.db \
  "SELECT * FROM knowledge_cards WHERE tags LIKE '%python%'"
```

---

## 📊 Implementation Roadmap

### Phase 1: MVP (Weeks 1-3)
- ✅ Basic marker detection
- ✅ SQLite storage with FTS5
- ✅ Obsidian markdown export
- ✅ Manual quality review workflow

**Deliverables:**
- `obsidian_extract.py` (core implementation)
- Database schema and migration
- Obsidian vault template

### Phase 2: Measurement (3 months)
- Track knowledge card volume (10-20/week)
- Monitor reuse frequency (5+ per card/month)
- Measure review approval rate (70%+)
- Assess graph utility (50+ connections)

**Decision Gate:** ROI > 0 ✓/✗

### Phase 3: Full Version (if ROI > 0)
- Visual Obsidian graph coloring (auto vs human)
- Automated weekly/monthly exports
- Claude Code terminal hook integration
- Advanced search with relevance ranking
- Knowledge card cross-linking and relationships

---

## 🐛 Troubleshooting

### No cards extracted

**Problem:** "No knowledge cards found"

**Causes:**
1. Missing `[EXTRACT_AS_KNOWLEDGE]` markers
2. Content is too short (< 50 chars)
3. Markers are malformed

**Solution:**
```bash
# Verify marker format
grep -n "EXTRACT_AS_KNOWLEDGE" your_file.txt

# Test with minimal example
obsidian-extract extract --text "[EXTRACT_AS_KNOWLEDGE]
This is a test knowledge card with enough content to meet the minimum length requirement.
#test
[/EXTRACT_AS_KNOWLEDGE]"
```

### Database locked

**Problem:** "Database is locked"

**Cause:** Multiple processes accessing database simultaneously

**Solution:**
```bash
# Wait a moment and retry
sleep 2 && obsidian-extract search "your-query"

# Or close other processes accessing the database
lsof ~/scripts/LLMLogger/knowledge.db
```

### Export not working

**Problem:** "Exported 0 cards to vault"

**Cause:**
1. Vault path is incorrect
2. No cards in database
3. Permission denied

**Solution:**
```bash
# Check vault path
ls -la ~/Obsidian/MyVault/

# Verify cards exist
obsidian-extract search "*" --limit 5

# Check permissions
touch ~/Obsidian/MyVault/test.md && rm ~/Obsidian/MyVault/test.md
```

### Search returns no results

**Problem:** Empty search results

**Causes:**
1. Query is too specific
2. Database not indexed
3. FTS5 syntax error

**Solution:**
```bash
# Try simpler query
obsidian-extract search "python"

# Rebuild FTS5 index (manual)
sqlite3 ~/scripts/LLMLogger/knowledge.db << EOF
DROP TABLE knowledge_fts;
CREATE VIRTUAL TABLE knowledge_fts USING fts5(title, content, tags);
INSERT INTO knowledge_fts SELECT title, content, tags FROM knowledge_cards;
EOF
```

---

## 📚 Examples

### Example 1: Capture Code Pattern

```
During Claude Code session:

[EXTRACT_AS_KNOWLEDGE]
# Python Context Manager Pattern

Context managers ensure resource cleanup via __enter__ and __exit__.

Example:
```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect('db.sqlite')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# Usage:
with DatabaseConnection() as db:
    db.execute("SELECT * FROM users")
```

Benefits:
- Guaranteed cleanup even if exception occurs
- Cleaner syntax than try/finally
- Better readability

#python #design-patterns #best-practices
[/EXTRACT_AS_KNOWLEDGE]

Command:
$ obsidian-extract extract --text "<above>"
✅ Extracted 1 card, stored 1
   → abc123def
```

### Example 2: Monthly Review Workflow

```bash
# Check status
$ obsidian-extract review
📊 Monthly Review Check
   Unreviewed: 22
   Accumulated days: 30
   ⚠️  22 cards pending review
   Recommendation: REVIEW

# Manually review in Obsidian (open vault)
# Then mark each reviewed card:

$ obsidian-extract mark abc123 --approved --notes "Verified with Python 3.10"
✅ Approved: abc123

$ obsidian-extract mark def456 --approved --notes "Still relevant"
✅ Approved: def456

$ obsidian-extract mark ghi789 --rejected --notes "Outdated, replaced by newer pattern"
❌ Rejected: ghi789

# Export only approved cards for final vault
$ obsidian-extract export ~/Obsidian/MyVault --reviewed-only
✅ Exported 21 cards to ~/Obsidian/MyVault/Knowledge Cards
```

### Example 3: Knowledge Reuse Across Sessions

```bash
# In a new Claude Code session, search previous knowledge:

$ obsidian-extract search "database optimization"
🔍 Found 2 results:

📝 Database Query Optimization Tips (abc456)
   Use EXPLAIN QUERY PLAN to analyze query performance...

📝 PostgreSQL Indexing Strategy (def789)
   B-tree indexes for equality/range queries...

# Copy relevant knowledge into current work, properly attributed
```

---

## 🔐 Security & Privacy

### Data Storage
- All data stored locally in SQLite (no cloud sync)
- Database location: `~/scripts/LLMLogger/knowledge.db`
- No personal data transmitted

### Access Control
- File permissions: `600` (read/write owner only)
- Optional: Encrypt database with SQLite encryption

### Audit Trail
- All edits tracked by extraction timestamp
- Review notes record who reviewed each card
- Export includes full metadata for traceability

---

## 📞 Support

### Common Issues Checklist

- [ ] Python 3.8+ installed? `python3 --version`
- [ ] Script executable? `ls -la /Users/in/ai-agent-experiment/tools/obsidian_extract.py`
- [ ] Database exists? `ls -la ~/scripts/LLMLogger/knowledge.db`
- [ ] Vault path correct? `ls -la ~/Obsidian/MyVault`
- [ ] No duplicate markers? `grep -c "EXTRACT_AS_KNOWLEDGE" file.txt`

### More Resources

- SQLite FTS5 docs: https://www.sqlite.org/fts5.html
- Obsidian vault structure: https://help.obsidian.md/Getting+started/Create+a+vault
- Claude Code integration: See parent CLAUDE.md

---

## 📝 Version Info

- **Version**: 1.0.0
- **Created**: 2026-03-06
- **Python**: 3.8+
- **Database**: SQLite 3.x with FTS5
- **Platforms**: macOS, Linux (Windows with WSL)
