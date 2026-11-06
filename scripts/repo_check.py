"""Keep the public overview minimal, English-only and free of local links."""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

allowed = {
    'README.md', 'LICENSE', '.gitignore', '.gitattributes',
    'assets/grade-banner.svg', 'assets/NOTICE.md', 'assets/Nacelle-OFL.txt',
    '.github/workflows/checks.yml', 'scripts/repo_check.py',
}
files = set(filter(None, subprocess.check_output(
    ['git', 'ls-files', '-z'], text=True).split('\0')))
errors = []
if files != allowed:
    errors.append('Unexpected publication contents: ' + repr(sorted(files ^ allowed)))
for name in sorted(files):
    text = Path(name).read_text(encoding='utf-8-sig')
    if re.search(r'[\u0400-\u052f]', text):
        errors.append('Cyrillic text: ' + name)
    if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})', text):
        errors.append('Possible credential: ' + name)
    if name.endswith('.md'):
        if re.search(r'C:[/\\]Users[/\\]', text):
            errors.append('Machine-specific path: ' + name)
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            parsed = urlsplit(target)
            if parsed.scheme:
                if parsed.scheme != 'https':
                    errors.append('Non-HTTPS link: ' + target)
            elif parsed.path and not (Path(name).parent / unquote(parsed.path)).exists():
                errors.append('Broken local link: ' + target)
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(files)} approved files, English-only text and valid local links.')
