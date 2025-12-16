#!/usr/bin/env python3
import os
import sys
import requests


def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(template: str, release: str, desc: str, code: str) -> str:
    return (
        template.replace("{{RELEASE}}", release)
        .replace("{{DESCRICAO_RELEASE}}", desc)
        .replace("{{CODIGO}}", code)
    )


def ensure_provider_suffix(model: str) -> str:
    # Se já vier com :publicai ou :hf-inference, respeita
    if ":" in model:
        return model
    # Padrão: hf-inference
    return f"{model}:hf-inference"


def call_hf_router_chat(model: str, prompt: str, token: str) -> str:
    url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": ensure_provider_suffix(model),
        "messages": [
            {
                "role": "system",
                "content": (
                    "Responda somente com CSV separado por ponto e vírgula. "
                    "Não use markdown. Não escreva explicações. "
                    "Não escreva tags como <think>. "
                    "Não repita o cabeçalho."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 900,
        "temperature": 0.2,
        "stream": False,
    }

    print("Chamando:", url)
    print("Modelo:", payload["model"])

    r = requests.post(url, headers=headers, json=payload, timeout=600)

    if r.status_code != 200:
        raise RuntimeError(f"Erro HF {r.status_code}: {r.text[:800]}")

    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Resposta inesperada: {data}")


def append_csv(out_path: str, csv_text: str, release: str, desc: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    write_header = not os.path.exists(out_path) or os.path.getsize(out_path) == 0
    header = "Release;DescricaoRelease;Categoria;CodeSmell;Justificativa\n"

    kept_lines = []
    for raw in csv_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("<think>") or line.startswith("</think>"):
            continue
        if line.lower().startswith("release;"):
            continue
        if ";" not in line:
            continue
        kept_lines.append(line)

    if not kept_lines:
        kept_lines.append(
            f"{release};{desc};NENHUM;NENHUM;Nenhum code smell identificado"
        )

    with open(out_path, "a", encoding="utf-8", newline="") as f:
        if write_header:
            f.write(header)
        if kept_lines:
            f.write("\n".join(kept_lines) + "\n")


def main():
    if len(sys.argv) < 7:
        print("Uso:")
        print(
            "python scripts/run_hf.py <modelo> <release> <descricao> <arquivo_codigo> <arquivo_prompt> <saida_csv>"
        )
        sys.exit(1)

    model = sys.argv[1]
    release = sys.argv[2]
    desc = sys.argv[3]
    code_path = sys.argv[4]
    prompt_path = sys.argv[5]
    out_path = sys.argv[6]

    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError('HF_TOKEN não definido. No PowerShell: $env:HF_TOKEN="hf_..."')

    template = load_prompt_template(prompt_path)

    with open(code_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # evita prompt gigante e reduz chance de 504 ou resposta cortada
    MAX_CHARS = 25000
    if len(code) > MAX_CHARS:
        code = code[:MAX_CHARS]

    prompt = build_prompt(template, release, desc, code)
    result = call_hf_router_chat(model, prompt, token)

    append_csv(out_path, result, release, desc)

    print(f"OK: resultado acrescentado em {out_path}")


if __name__ == "__main__":
    main()
