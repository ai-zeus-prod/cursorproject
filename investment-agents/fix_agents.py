#!/usr/bin/env python3
"""
Fix Python path imports in all agent files
"""

from pathlib import Path

agent_files = [
    'agents/agent_2_fundamental.py',
    'agents/agent_3_technical.py',
    'agents/agent_6_orchestrator.py',
]

path_fix = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""

for agent_file in agent_files:
    filepath = Path(agent_file)
    if not filepath.exists():
        print(f"Skipping {agent_file} - not found")
        continue

    content = filepath.read_text()

    # Check if already fixed
    if 'sys.path.insert(0,' in content:
        print(f"✓ {agent_file} already fixed")
        continue

    # Find the first import statement
    lines = content.split('\n')
    insert_pos = 0

    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_pos = i
            break

    # Insert path fix before first import
    lines.insert(insert_pos, path_fix.rstrip())

    # Write back
    filepath.write_text('\n'.join(lines))
    print(f"✓ Fixed {agent_file}")

print("\nAll agents fixed!")
