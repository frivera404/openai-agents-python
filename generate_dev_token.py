"""Generate a short-lived dev JWT and write it to `.token.txt`.

Usage: .venv\Scripts\python.exe generate_dev_token.py
"""

from workflows.agent_system.auth import create_jwt


def main() -> None:
    t = create_jwt({"user_id": "dev", "sub": "dev", "role": "admin"})
    with open('.token.txt', 'w', encoding='utf-8') as f:
        f.write(t)
    print('WROTE_TOKEN')


if __name__ == '__main__':
    main()
