"""Upload a JSONL file and create a fine-tune job via the OpenAI REST API.

This script uses `requests` and implements simple retry/backoff for transient
errors (5xx/520). It supports a dry-run mode that prints the curl commands you
can run manually.

Usage:
    python scripts/upload_and_create_finetune.py \
        --file data/autonomy_train_v3.jsonl \
        --model gpt-4o-mini

The script requires `OPENAI_API_KEY` to be set in the environment.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import requests


def upload_file(api_key: str, file_path: str, max_retries: int = 5) -> str | None:
    url = "https://api.openai.com/v1/files"
    headers = {"Authorization": f"Bearer {api_key}"}
    for attempt in range(1, max_retries + 1):
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/jsonl")}
                data = {"purpose": "fine-tune"}
                r = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            if r.status_code in (200, 201):
                j = r.json()
                print("Upload successful, response id:", j.get("id"))
                return j.get("id")
            elif 500 <= r.status_code < 600 or r.status_code in (520,):
                print(
                    "Transient server error (status=", r.status_code, "), attempt",
                    f"{attempt}/{max_retries}",
                )
            else:
                print(f"Upload failed (status={r.status_code}): {r.text}")
                return None
        except requests.RequestException as e:
            print(f"Request error on upload attempt {attempt}/{max_retries}: {e}")

        if attempt < max_retries:
            backoff = 2**attempt
            print(f"Retrying in {backoff}s...")
            time.sleep(backoff)

    print("Exceeded max retries for upload.")
    return None


def create_finetune(api_key: str, file_id: str, model: str, max_retries: int = 5) -> dict | None:
    url = "https://api.openai.com/v1/fine_tunes"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"training_file": file_id, "model": model}

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code in (200, 201):
                print("Fine-tune job created:", r.json())
                return r.json()
            elif 500 <= r.status_code < 600 or r.status_code in (520,):
                print(
                    "Transient server error creating fine-tune (status=", r.status_code,
                    "), attempt", f"{attempt}/{max_retries}",
                )
            else:
                print(f"Failed to create fine-tune (status={r.status_code}): {r.text}")
                return None
        except requests.RequestException as e:
            print(f"Request error on create attempt {attempt}/{max_retries}: {e}")

        if attempt < max_retries:
            backoff = 2**attempt
            print(f"Retrying in {backoff}s...")
            time.sleep(backoff)

    print("Exceeded max retries for creating fine-tune job.")
    return None


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="JSONL file to upload")
    p.add_argument("--model", default="gpt-4.1", help="Model to fine-tune")
    p.add_argument(
        "--dry-run", action="store_true", help="Print curl commands instead of calling API"
    )
    args = p.parse_args(argv)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set in environment. Aborting.")
        sys.exit(1)

    if args.dry_run:
        print("Dry-run: run the following commands to upload and create fine-tune:")
        print()
        print(
            "curl -X POST https://api.openai.com/v1/files "
            "-H 'Authorization: Bearer $OPENAI_API_KEY' "
            f"-F 'purpose=fine-tune' -F 'file=@{args.file}'"
        )
        print()
        print(
            "curl -X POST https://api.openai.com/v1/fine_tunes "
            "-H 'Authorization: Bearer $OPENAI_API_KEY' "
            "-H 'Content-Type: application/json' "
            + (
                '{"training_file": "<FILE_ID>", "model": "' + args.model + '"}'
            )
        )
        return

    print("Uploading file:", args.file)
    file_id = upload_file(api_key, args.file)
    if not file_id:
        print("Upload failed — aborting fine-tune creation.")
        return

    print("Creating fine-tune with file id:", file_id)
    create_finetune(api_key, file_id, args.model)


if __name__ == "__main__":
    main()
