#!/usr/bin/env python3
import csv
import io
import os
import sys
import tarfile
import requests

from run_hf import (
    append_csv,
    build_prompt,
    call_hf_router_chat,
    load_prompt_template,
)


MAX_CHARS = 25_000
MAX_FILE_BYTES = 200_000
ALLOWED_EXTS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".java",
    ".kt",
    ".kts",
    ".rb",
    ".go",
    ".rs",
    ".php",
    ".cs",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",
    ".scala",
    ".swift",
    ".m",
    ".mm",
    ".sh",
    ".ps1",
}


def download_tarball(url: str, token: str | None) -> bytes:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, headers=headers, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Erro {r.status_code} ao baixar {url}: {r.text[:300]}")
    return r.content


def extract_text_from_tarball(blob: bytes, max_chars: int = MAX_CHARS) -> str:
    buf = io.BytesIO(blob)
    texts: list[str] = []
    total = 0

    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            if member.size > MAX_FILE_BYTES:
                continue

            # cheap binary guard by extension
            name_lower = member.name.lower()
            if "." in name_lower:
                _, ext = os.path.splitext(name_lower)
                if ext and ext not in ALLOWED_EXTS:
                    continue

            extracted = tar.extractfile(member)
            if not extracted:
                continue
            try:
                content = extracted.read().decode("utf-8", errors="ignore")
            except Exception:
                continue
            if not content.strip():
                continue

            remaining = max_chars - total
            if remaining <= 0:
                break

            chunk = content[:remaining]
            texts.append(f"// {member.name}\n{chunk}")
            total += len(chunk)

            if total >= max_chars:
                break

    return "\n\n".join(texts)


def main():
    if len(sys.argv) < 5:
        print("Uso:")
        print(
            "python scripts/run_hf_batch.py <modelo> <csv_releases> <arquivo_prompt> <saida_csv>"
        )
        sys.exit(1)

    model = sys.argv[1]
    releases_csv = sys.argv[2]
    prompt_path = sys.argv[3]
    out_path = sys.argv[4]

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise RuntimeError('HF_TOKEN nao definido. No PowerShell: $env:HF_TOKEN="hf_..."')

    gh_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    template = load_prompt_template(prompt_path)

    with open(releases_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            release = row.get("tag_name") or row.get("name") or f"release_{idx}"
            desc = row.get("name") or release
            tar_url = row.get("tarball_url")

            if not tar_url:
                print(f"[{idx}] Pulando {release}: sem tarball_url")
                continue

            print(f"[{idx}] Baixando {release} de {tar_url}")
            blob = download_tarball(tar_url, gh_token)

            code = extract_text_from_tarball(blob, MAX_CHARS)
            prompt = build_prompt(template, release, desc, code)
            result = call_hf_router_chat(model, prompt, hf_token)
            append_csv(out_path, result, release, desc)
            print(f"[{idx}] OK -> {out_path}")


if __name__ == "__main__":
    main()
