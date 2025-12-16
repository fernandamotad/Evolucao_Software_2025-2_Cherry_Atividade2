#!/usr/bin/env python3
import csv
import os
import sys
import requests
from datetime import datetime

API_BASE = "https://api.github.com"


def gh_get(url: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "evolucao-software-atividade2",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, headers=headers, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Erro {r.status_code} ao chamar {url}: {r.text[:300]}")
    return r.json()


def list_all_releases(owner: str, repo: str, token: str | None):
    releases = []
    page = 1
    per_page = 100

    while True:
        url = f"{API_BASE}/repos/{owner}/{repo}/releases?per_page={per_page}&page={page}"
        data = gh_get(url, token)
        if not data:
            break
        releases.extend(data)
        page += 1

    return releases


def normalize_release(r: dict):
    return {
        "id": r.get("id"),
        "tag_name": r.get("tag_name"),
        "name": r.get("name"),
        "published_at": r.get("published_at"),
        "created_at": r.get("created_at"),
        "draft": r.get("draft"),
        "prerelease": r.get("prerelease"),
        "html_url": r.get("html_url"),
        "tarball_url": r.get("tarball_url"),
        "zipball_url": r.get("zipball_url"),
    }


def write_csv(path: str, rows: list[dict]):
    if not rows:
        raise RuntimeError("Nenhuma release encontrada para exportar.")

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sample_systematic(rows: list[dict], sample_rate: float):
    if not (0 < sample_rate <= 1):
        raise ValueError("sample_rate deve estar entre 0 e 1. Ex: 0.3 para 30%")

    n = len(rows)
    sample_size = max(1, int(round(n * sample_rate)))
    step = n / sample_size

    chosen = []
    idx = 0.0
    used = set()

    for _ in range(sample_size):
        i = int(round(idx))
        if i >= n:
            i = n - 1

        while i in used and i < n - 1:
            i += 1

        used.add(i)
        chosen.append(rows[i])
        idx += step

    return chosen


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 export_releases_csv.py <owner> <repo> [sample_rate]")
        print("Ex:  python3 export_releases_csv.py CherryHQ cherry-studio 0.3")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    sample_rate = float(sys.argv[3]) if len(sys.argv) >= 4 else None

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    raw = list_all_releases(owner, repo, token)
    rows = [normalize_release(r) for r in raw]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_all = os.path.join("data", f"releases_{owner}_{repo}_{timestamp}.csv")
    write_csv(out_all, rows)
    print(f"OK: exportou {len(rows)} releases em {out_all}")

    if sample_rate is not None:
        sampled = sample_systematic(rows, sample_rate)
        out_sample = os.path.join(
            "data",
            f"releases_{owner}_{repo}_{timestamp}_sample_{int(sample_rate * 100)}pct.csv",
        )
        write_csv(out_sample, sampled)
        print(f"OK: exportou amostra {len(sampled)} releases em {out_sample}")


if __name__ == "__main__":
    main()
