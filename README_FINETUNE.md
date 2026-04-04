Fine-tune guide and manual upload instructions
=============================================

This guide shows how to upload a generated JSONL dataset and create a fine-tune
job using the OpenAI REST API. It includes a script `scripts/upload_and_create_finetune.py`
that implements retries and a dry-run mode.

Quick manual curl steps
-----------------------

1. Set your API key in the environment:

```powershell
$env:OPENAI_API_KEY="sk-..."
```

2. Upload the file (replace path):

```bash
curl -X POST https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "purpose=fine-tune" \
  -F "file=@data/autonomy_train_v3.jsonl"
```

Note the `id` field in the response (e.g. `file-...`).

3. Create the fine-tune job (replace `<FILE_ID>` and `model`):

```bash
curl -X POST https://api.openai.com/v1/fine_tunes \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"training_file": "<FILE_ID>", "model": "gpt-4.1"}'
```

If the API returns 5xx/520 occasionally, retry after a short delay. If you
continue to see 5xx errors, the OpenAI service may be experiencing an outage.

Using the helper script
------------------------

The repository includes `scripts/upload_and_create_finetune.py` which:

- Uploads the file with retries.
- Attempts to create the fine-tune job with retries.
- Has a `--dry-run` mode to print the curl commands instead of calling the API.

Run example:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:PYTHONPATH="src"; .venv\Scripts\python scripts/upload_and_create_finetune.py --file data/autonomy_train_v3.jsonl --model gpt-4.1
```

Recommendation
--------------

- If you want me to continue retrying automatically, I can re-run the script
  now or schedule repeated attempts with backoff until success.
- If you'd prefer to avoid changing package versions in the venv (we previously
  downgraded `openai` and it caused dependency conflicts), keep `openai>=2.9.0`
  and use this uploader script (it uses `requests` and does not depend on the
  `openai` Python SDK).
