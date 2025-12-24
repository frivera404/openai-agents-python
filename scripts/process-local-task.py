import json
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path so scripts can be run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_private_i.app import build_system


def main(path_str: str):
    p = Path(path_str)
    if not p.exists():
        print('Task file not found:', p)
        return 2
    payload = json.loads(p.read_text(encoding='utf-8'))
    orch, store = build_system()
    print('Running task:', payload.get('task_id'))
    result = orch.run_task(payload)
    print('Result:', result.get('task_id'), result.get('status'))
    print('History:')
    for h in result.get('history', []):
        print('-', h)
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: process-local-task.py <path_to_task.json>')
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
