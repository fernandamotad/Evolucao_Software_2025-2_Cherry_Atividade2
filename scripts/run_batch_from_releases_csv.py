#!/usr/bin/env python3
import csv
import os
import sys
import subprocess


def find_latest_sample_csv(data_dir: str) -> str:
    files = [
        f for f in os.listdir(data_dir)
        if f.endswith(".csv") and "_sample_30pct" in f
    ]
    if not files:
        raise RuntimeError(
            f"Nenhum arquivo '*_sample_30pct.csv' encontrado em {data_dir}"
        )
    files.sort()
    return os.path.join(data_dir, files[-1])


def main():
    if len(sys.argv) < 5:
        print(
            "Uso:\n"
            "python scripts/run_batch_from_releases_csv.py "
            "<modelo> <csv_releases_30pct> <arquivo_codigo> <arquivo_prompt> [saida_csv]\n\n"
            "Ex:\n"
            "python scripts/run_batch_from_releases_csv.py "
            "HuggingFaceTB/SmolLM3-3B:hf-inference "
            "data/releases_..._sample_30pct.csv "
            "releases/editor.ts "
            "prompt/code_smells_prompt.txt "
            "analises/smollm3_resultados.csv"
        )
        sys.exit(1)

    model = sys.argv[1]
    releases_csv = sys.argv[2]
    code_file = sys.argv[3]
    prompt_file = sys.argv[4]
    out_csv = sys.argv[5] if len(sys.argv) >= 6 else None

    if releases_csv == "AUTO":
        releases_csv = find_latest_sample_csv("data")

    if out_csv is None:
        safe_model = model.replace("/", "_").replace(":", "_")
        out_csv = os.path.join("analises", f"{safe_model}_resultados.csv")

    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    if not os.path.exists(releases_csv):
        raise RuntimeError(f"CSV de releases não encontrado: {releases_csv}")

    if not os.path.exists(code_file):
        raise RuntimeError(f"Arquivo de código não encontrado: {code_file}")

    if not os.path.exists(prompt_file):
        raise RuntimeError(f"Arquivo de prompt não encontrado: {prompt_file}")

    with open(releases_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise RuntimeError("CSV de releases está vazio.")

    total = len(rows)
    print(f"OK: {total} releases carregadas de {releases_csv}")
    print(f"Modelo: {model}")
    print(f"Saída: {out_csv}")

    for i, row in enumerate(rows, start=1):
        release = (row.get("tag_name") or row.get("name") or str(row.get("id") or "")).strip()
        desc = (row.get("name") or "").strip()

        if not release:
            release = f"release_{i}"

        print(f"[{i}/{total}] Rodando release {release}")

        subprocess.run(
            [
                sys.executable,
                "scripts/run_hf.py",
                model,
                release,
                desc,
                code_file,
                prompt_file,
                out_csv,
            ],
            check=True,
        )

    print("Finalizado.")


if __name__ == "__main__":
    main()
