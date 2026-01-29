"""
Remove all emojis from the codebase for Windows compatibility.
"""

import os
import re
from pathlib import Path

# Broad emoji stripper for anything missed by REPLACEMENTS.
# Includes:
# - most emoji blocks (U+1F000..U+1FAFF)
# - Dingbats/Misc Symbols (U+2600..U+27BF)
# - Variation Selector-16 (U+FE0F) + ZWJ (U+200D) which combine emojis
EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]")

# Replacement map (emoji -> text equivalent)
REPLACEMENTS = {
    '✅': '[DONE]',
    '❌': '[FAIL]',
    '🚧': '[WIP]',
    '📋': '[TODO]',
    '⭐': '[*]',
    '💥': '[ERROR]',
    '⏭️': '[SKIP]',
    '❓': '[?]',
    '🔍': '[SEARCH]',
    '🧪': '[TEST]',
    '🎯': '[TARGET]',
    '🚀': '[LAUNCH]',
    '📊': '[STATS]',
    '📚': '[DOCS]',
    '🎉': '[SUCCESS]',
    '✨': '[NEW]',
    '📦': '[PACKAGE]',
    '🔧': '[TOOLS]',
    '📈': '[PERF]',
    '🎓': '[LEARN]',
    '⚡': '[FAST]',
    '🌐': '[WEB]',
    '💰': '[COST]',
    '✓': '[OK]',
    '→': '->',
    '↓': 'v',
    '▶': '>',
    '⚠️': '[WARNING]',
    '💡': '[TIP]',
    '🔑': '[KEY]',
    '📝': '[NOTE]',
    '🎨': '[STYLE]',
}

def remove_emojis_from_file(filepath):
    """Remove emojis from a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace each emoji with text equivalent
        for emoji, replacement in REPLACEMENTS.items():
            content = content.replace(emoji, replacement)

        # Strip any remaining emoji-like characters
        content = EMOJI_RE.sub("", content)

        # If content changed, write it back
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Remove emojis from all files in the project"""
    # repo root: tools/scripts/remove_emojis.py -> tools/scripts -> tools -> repo root
    project_root = Path(__file__).resolve().parents[2]

    # File patterns to process
    patterns = ['**/*.md', '**/*.py', '**/*.txt']

    # Paths to skip (avoid binary/media and large generated outputs)
    skip_parts = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "media",
        "giffolder",
        "output",
        ".mypy_cache",
        ".pytest_cache",
    }

    # Files to skip
    skip_files = {"remove_emojis.py"}

    modified_files = []

    for pattern in patterns:
        for filepath in project_root.glob(pattern):
            # Skip if in skip list or in skipped directories
            if any(part in skip_parts for part in filepath.parts):
                continue
            if filepath.name in skip_files:
                continue

            if filepath.is_file():
                if remove_emojis_from_file(filepath):
                    modified_files.append(filepath)
                    print(f"Modified: {filepath.relative_to(project_root)}")

    print(f"\n\nTotal files modified: {len(modified_files)}")

    if modified_files:
        print("\nModified files:")
        for f in modified_files:
            print(f"  - {f.relative_to(project_root)}")

if __name__ == "__main__":
    main()
