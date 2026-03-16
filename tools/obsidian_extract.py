#!/usr/bin/env python3
"""
Obsidian × Claude Code Integration Tool
Extract knowledge cards from Claude Code logs and export to Obsidian vault
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from hashlib import sha256
import sys
import argparse

@dataclass
class KnowledgeCard:
    """Knowledge card extracted from Claude Code logs"""
    id: str
    title: str
    content: str
    source_log: str
    extracted_at: str
    tags: List[str]
    reviewed: bool = False
    review_notes: str = ""
    obsidian_node_id: str = ""  # For visual graph distinction

class KnowledgeCardExtractor:
    """Main extraction engine for [EXTRACT_AS_KNOWLEDGE] markers"""

    MARKER_PATTERN = r'\[EXTRACT_AS_KNOWLEDGE\](.*?)\[/EXTRACT_AS_KNOWLEDGE\]'
    TAGS_PATTERN = r'#\w+'
    MIN_CONTENT_LENGTH = 50

    def __init__(self, db_path: str = None):
        """Initialize extractor with optional SQLite database"""
        self.db_path = db_path or self._get_default_db_path()
        self._init_database()

    @staticmethod
    def _get_default_db_path() -> str:
        """Get default database path from LLMLogger"""
        home = Path.home()
        return str(home / "scripts" / "LLMLogger" / "knowledge.db")

    def _init_database(self):
        """Initialize SQLite FTS5 database for knowledge cards"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_cards (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_log TEXT,
                extracted_at TEXT,
                tags TEXT,
                reviewed INTEGER DEFAULT 0,
                review_notes TEXT,
                obsidian_node_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
            USING fts5(title, content, tags)
        ''')

        conn.commit()
        conn.close()

    def extract_from_text(self, text: str, source: str = "unknown") -> List[KnowledgeCard]:
        """
        Extract knowledge cards from text containing [EXTRACT_AS_KNOWLEDGE] markers
        """
        cards = []
        matches = re.finditer(self.MARKER_PATTERN, text, re.DOTALL)

        for match in matches:
            content = match.group(1).strip()

            # Validation
            if len(content) < self.MIN_CONTENT_LENGTH:
                print(f"⚠️  Skipped: content too short ({len(content)} chars)")
                continue

            card = self._create_card(content, source)
            if card:
                cards.append(card)

        return cards

    def _create_card(self, content: str, source: str) -> Optional[KnowledgeCard]:
        """Create a knowledge card from extracted content"""
        # Extract title (first line or up to 100 chars)
        lines = content.split('\n')
        title = lines[0][:100]

        # Extract tags
        tags = re.findall(self.TAGS_PATTERN, content)
        tags = list(set(tags))  # Deduplicate

        # Generate deterministic ID
        card_id = sha256(
            f"{title}{datetime.now().date()}".encode()
        ).hexdigest()[:12]

        # Create Obsidian node ID (for visual distinction in graph)
        obsidian_node_id = f"auto-{card_id}"

        return KnowledgeCard(
            id=card_id,
            title=title,
            content=content,
            source_log=source,
            extracted_at=datetime.now().isoformat(),
            tags=tags,
            obsidian_node_id=obsidian_node_id
        )

    def store_cards(self, cards: List[KnowledgeCard]) -> Tuple[int, List[str]]:
        """Store knowledge cards in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stored_ids = []
        duplicate_count = 0

        for card in cards:
            try:
                # Check if card already exists
                cursor.execute('SELECT id FROM knowledge_cards WHERE id = ?', (card.id,))
                if cursor.fetchone():
                    duplicate_count += 1
                    continue

                # Store card
                cursor.execute('''
                    INSERT INTO knowledge_cards
                    (id, title, content, source_log, extracted_at, tags, obsidian_node_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    card.id, card.title, card.content, card.source_log,
                    card.extracted_at, json.dumps(card.tags), card.obsidian_node_id
                ))

                # Also index in FTS5
                cursor.execute('''
                    INSERT INTO knowledge_fts (title, content, tags)
                    VALUES (?, ?, ?)
                ''', (card.title, card.content, ' '.join(card.tags)))

                stored_ids.append(card.id)

            except Exception as e:
                print(f"❌ Error storing card {card.id}: {e}")

        conn.commit()
        conn.close()

        if duplicate_count > 0:
            print(f"⚠️  {duplicate_count} duplicate cards skipped")

        return len(stored_ids), stored_ids

    def search_cards(self, query: str, limit: int = 10) -> List[Dict]:
        """Search knowledge cards using FTS5"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT k.id, k.title, k.content, k.extracted_at, k.tags
            FROM knowledge_fts AS f
            JOIN knowledge_cards AS k ON f.rowid = (
                SELECT rowid FROM knowledge_fts WHERE
                title = k.title AND content = k.content
            )
            WHERE knowledge_fts MATCH ?
            LIMIT ?
        ''', (query, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'extracted_at': row[3],
                'tags': json.loads(row[4]) if row[4] else []
            })

        conn.close()
        return results

    def export_to_obsidian(self, vault_path: str, reviewed_only: bool = False) -> Tuple[int, str]:
        """
        Export knowledge cards to Obsidian vault as markdown notes
        Returns: (count, export_path)
        """
        vault_path = Path(vault_path)
        knowledge_dir = vault_path / "Knowledge Cards"
        knowledge_dir.mkdir(exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query based on filter
        if reviewed_only:
            cursor.execute('SELECT * FROM knowledge_cards WHERE reviewed = 1')
        else:
            cursor.execute('SELECT * FROM knowledge_cards')

        rows = cursor.fetchall()
        exported_count = 0

        for row in rows:
            card_id, title, content, source, extracted_at, tags, reviewed, review_notes, node_id = row

            # Create markdown frontmatter
            tags_list = json.loads(tags) if tags else []
            frontmatter = f"""---
id: {card_id}
node_type: {'human-extracted' if reviewed else 'auto-extracted'}
node_id: {node_id}
source: {source}
extracted_at: {extracted_at}
reviewed: {reviewed}
tags: {json.dumps(tags_list)}
---

# {title}

## Content
{content}

## Metadata
- **Extracted**: {extracted_at}
- **Source**: {source}
- **Status**: {'✅ Reviewed' if reviewed else '⏳ Pending Review'}
{"- **Review Notes**: " + review_notes if review_notes else ""}
- **Tags**: {', '.join(tags_list) if tags_list else "None"}

## References
*Add backlinks here for Obsidian graph visualization*
"""

            # Write file (auto = green node, human = blue node)
            node_prefix = "human" if reviewed else "auto"
            filename = f"{node_prefix}-{card_id}-{title[:50]}.md"
            filepath = knowledge_dir / filename

            filepath.write_text(frontmatter)
            exported_count += 1

        conn.close()

        return exported_count, str(knowledge_dir)


class ObsidianExportManager:
    """Manage Obsidian vault integration and scheduling"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.extractor = KnowledgeCardExtractor()

    def monthly_review_check(self) -> Dict:
        """
        Monthly quality review check (60 min allocated)
        Returns statistics and flagged cards for manual review
        """
        conn = sqlite3.connect(self.extractor.db_path)
        cursor = conn.cursor()

        # Get unreviewed cards
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT DATE(extracted_at))
            FROM knowledge_cards
            WHERE reviewed = 0
        ''')
        unreviewed_count, days_since_extraction = cursor.fetchone()

        # Flag for review if accumulation is excessive
        flags = []
        if unreviewed_count > 20:
            flags.append(f"⚠️  {unreviewed_count} cards pending review")

        stats = {
            'unreviewed_count': unreviewed_count,
            'days_accumulated': days_since_extraction or 0,
            'flags': flags,
            'recommended_action': 'REVIEW' if unreviewed_count > 10 else 'MONITOR'
        }

        conn.close()
        return stats

    def mark_reviewed(self, card_id: str, approved: bool = True, notes: str = ""):
        """Mark a card as reviewed and optionally add notes"""
        conn = sqlite3.connect(self.extractor.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE knowledge_cards
            SET reviewed = 1, review_notes = ?
            WHERE id = ?
        ''', (notes or "", card_id))

        conn.commit()
        conn.close()

        status = "✅ Approved" if approved else "❌ Rejected"
        print(f"{status}: {card_id}")


def main():
    """CLI interface for the extraction tool"""
    parser = argparse.ArgumentParser(
        description="Obsidian × Claude Code Knowledge Extraction Tool"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # extract command
    extract_parser = subparsers.add_parser('extract', help='Extract from log text')
    extract_parser.add_argument('--log-file', '-f', help='Input log file')
    extract_parser.add_argument('--text', '-t', help='Direct text input')
    extract_parser.add_argument('--source', '-s', default='claude-code-log')
    extract_parser.add_argument('--db', help='Database path')

    # export command
    export_parser = subparsers.add_parser('export', help='Export to Obsidian vault')
    export_parser.add_argument('vault_path', help='Path to Obsidian vault')
    export_parser.add_argument('--reviewed-only', action='store_true')
    export_parser.add_argument('--db', help='Database path')

    # search command
    search_parser = subparsers.add_parser('search', help='Search knowledge cards')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-l', type=int, default=10)
    search_parser.add_argument('--db', help='Database path')

    # review command
    review_parser = subparsers.add_parser('review', help='Monthly review check')
    review_parser.add_argument('--db', help='Database path')

    # mark command
    mark_parser = subparsers.add_parser('mark', help='Mark card as reviewed')
    mark_parser.add_argument('card_id', help='Card ID')
    mark_parser.add_argument('--approved', action='store_true', default=True)
    mark_parser.add_argument('--rejected', action='store_true')
    mark_parser.add_argument('--notes', '-n', help='Review notes')
    mark_parser.add_argument('--vault', '-v', help='Obsidian vault path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize extractor
    extractor = KnowledgeCardExtractor(args.db if hasattr(args, 'db') else None)

    if args.command == 'extract':
        # Get input text
        if args.log_file:
            text = Path(args.log_file).read_text()
        elif args.text:
            text = args.text
        else:
            print("❌ Provide either --log-file or --text")
            return

        cards = extractor.extract_from_text(text, args.source)
        if not cards:
            print("❌ No knowledge cards found")
            return

        stored, ids = extractor.store_cards(cards)
        print(f"✅ Extracted {len(cards)} cards, stored {stored}")
        for card_id in ids:
            print(f"   → {card_id}")

    elif args.command == 'export':
        manager = ObsidianExportManager(args.vault_path)
        count, path = extractor.export_to_obsidian(args.vault_path, args.reviewed_only)
        print(f"✅ Exported {count} cards to {path}")

    elif args.command == 'search':
        results = extractor.search_cards(args.query, args.limit)
        if not results:
            print("❌ No results found")
            return

        print(f"🔍 Found {len(results)} results:")
        for result in results:
            print(f"\n📝 {result['title']} ({result['id']})")
            print(f"   {result['content'][:100]}...")

    elif args.command == 'review':
        manager = ObsidianExportManager("")
        stats = manager.monthly_review_check()
        print(f"📊 Monthly Review Check")
        print(f"   Unreviewed: {stats['unreviewed_count']}")
        print(f"   Accumulated days: {stats['days_accumulated']}")
        if stats['flags']:
            for flag in stats['flags']:
                print(f"   {flag}")
        print(f"   Recommendation: {stats['recommended_action']}")

    elif args.command == 'mark':
        vault_path = args.vault if args.vault else str(Path.home() / "Obsidian")
        manager = ObsidianExportManager(vault_path)
        approved = not args.rejected
        manager.mark_reviewed(args.card_id, approved, args.notes or "")


if __name__ == '__main__':
    main()
