"""
Remove all emojis from the codebase for Windows compatibility.
"""

import os
import re
from pathlib import Path

# Emoji patterns to remove
EMOJI_PATTERNS = [
    r'✅',  r'❌',  r'🚧',  r'📋',  r'⭐',  r'💥',  r'⏭️',  r'❓',
    r'🔍',  r'🧪',  r'🎯',  r'🚀',  r'📊',  r'📚',  r'🎉',  r'✨',
    r'📦',  r'🔧',  r'📈',  r'🎓',  r'⚡',  r'🌐',  r'💰',  r'✓',
    r'→',  r'↓',  r'▶',  r'⚠️',  r'💡',  r'🔑',  r'📝',  r'🎨',
]

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
    project_root = Path(__file__).parent

    # File patterns to process
    patterns = ['**/*.md', '**/*.py', '**/*.txt']

    # Files to skip
    skip_files = {'remove_emojis.py', '.git'}

    modified_files = []

    for pattern in patterns:
        for filepath in project_root.glob(pattern):
            # Skip if in skip list or in .git directory
            if any(skip in str(filepath) for skip in skip_files):
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
