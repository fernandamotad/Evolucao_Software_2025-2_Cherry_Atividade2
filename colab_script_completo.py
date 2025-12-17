"""
🚀 ANÁLISE DE CODE SMELLS COM 3 MODELOS LLM
===============================================

INSTRUÇÕES DE USO NO GOOGLE COLAB:

1. Acesse: https://colab.research.google.com/
2. File → New notebook
3. Runtime → Change runtime type → GPU → Save
4. COPIE TODO ESTE ARQUIVO e cole na primeira célula do Colab
5. Execute a célula (Ctrl+Enter)
6. Siga as instruções que aparecerão na tela

Tempo estimado: ~1h15min com GPU
"""

# ============================================================================
# PASSO 1: VERIFICAR GPU E INSTALAR DEPENDÊNCIAS
# ============================================================================

print("🔧 Instalando dependências...")
import subprocess
subprocess.run(["pip", "install", "-q", "transformers", "accelerate", "torch"], check=True)

import torch
print(f"\n{'='*60}")
print("🎮 VERIFICAÇÃO DE GPU")
print(f"{'='*60}")
print(f"GPU disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memória: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("⚠️  ATENÇÃO: GPU não detectada! Vá em Runtime → Change runtime type → GPU")
    exit()

# ============================================================================
# PASSO 2: UPLOAD DOS ARQUIVOS
# ============================================================================

from google.colab import files
import os

# Criar estrutura de pastas
os.makedirs("data", exist_ok=True)
os.makedirs("releases", exist_ok=True)
os.makedirs("prompt", exist_ok=True)
os.makedirs("analises", exist_ok=True)

print(f"\n{'='*60}")
print("📤 UPLOAD DE ARQUIVOS")
print(f"{'='*60}\n")

print("1️⃣ Faça upload do CSV de releases:")
print("   Arquivo: releases_CherryHQ_cherry-studio_...sample_30pct.csv\n")
uploaded = files.upload()
for filename in uploaded.keys():
    os.rename(filename, f"data/{filename}")
    print(f"✅ {filename} salvo em data/\n")

print("2️⃣ Faça upload do código TypeScript:")
print("   Arquivo: editor.ts\n")
uploaded = files.upload()
for filename in uploaded.keys():
    os.rename(filename, f"releases/{filename}")
    print(f"✅ {filename} salvo em releases/\n")

print("3️⃣ Faça upload do prompt:")
print("   Arquivo: code_smells_prompt.txt\n")
uploaded = files.upload()
for filename in uploaded.keys():
    os.rename(filename, f"prompt/{filename}")
    print(f"✅ {filename} salvo em prompt/\n")

# ============================================================================
# PASSO 3: FUNÇÕES DE PROCESSAMENTO
# ============================================================================

import csv
from time import time
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(template: str, release: str, desc: str, code: str) -> str:
    return (
        template.replace("{{RELEASE}}", release)
        .replace("{{DESCRICAO_RELEASE}}", desc)
        .replace("{{CODIGO}}", code)
    )

def load_model(model_name: str):
    print(f"\n📥 Carregando: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True
    )
    print(f"✅ Modelo carregado!\n")
    return model, tokenizer

def generate_response(model, tokenizer, prompt: str) -> str:
    messages = [
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
    ]
    
    formatted_prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=900,
            temperature=0.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    return tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    ).strip()

def append_csv(out_path: str, csv_text: str, release: str, desc: str):
    write_header = not os.path.exists(out_path) or os.path.getsize(out_path) == 0
    header = "Release;DescricaoRelease;Categoria;CodeSmell;Justificativa\n"

    kept_lines = []
    for raw in csv_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("<think>") or line.startswith("</think>"):
            continue
        if line.lower().startswith("release;") or ";" not in line:
            continue
        kept_lines.append(line)

    if not kept_lines:
        kept_lines.append(f"{release};{desc};NENHUM;NENHUM;Nenhum code smell identificado")

    with open(out_path, "a", encoding="utf-8", newline="") as f:
        if write_header:
            f.write(header)
        if kept_lines:
            f.write("\n".join(kept_lines) + "\n")

# ============================================================================
# PASSO 4: CARREGAR DADOS
# ============================================================================

import glob

csv_files = glob.glob("data/*.csv")
code_files = glob.glob("releases/*.ts") + glob.glob("releases/*.js")
prompt_files = glob.glob("prompt/*.txt")

if not csv_files or not code_files or not prompt_files:
    print("❌ Erro: Arquivos não encontrados! Faça upload novamente.")
    exit()

RELEASES_CSV = csv_files[0]
CODE_FILE = code_files[0]
PROMPT_FILE = prompt_files[0]

with open(RELEASES_CSV, newline="", encoding="utf-8") as f:
    releases = list(csv.DictReader(f))

with open(CODE_FILE, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()[:20000]  # Limita a 20k chars

prompt_template = load_prompt_template(PROMPT_FILE)

print(f"\n{'='*60}")
print("📊 DADOS CARREGADOS")
print(f"{'='*60}")
print(f"✅ {len(releases)} releases encontradas")
print(f"✅ Código: {len(code)} caracteres")
print(f"✅ Prompt carregado\n")

# ============================================================================
# PASSO 5: PROCESSAR COM OS 3 MODELOS
# ============================================================================

MODELOS = [
    ("Qwen/Qwen2.5-0.5B-Instruct", "analises/qwen_resultados.csv"),
    ("microsoft/Phi-3-mini-4k-instruct", "analises/phi3_resultados.csv"),
    ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "analises/smollm17b_resultados.csv"),
]

for model_name, output_file in MODELOS:
    print(f"\n{'='*70}")
    print(f"🚀 PROCESSANDO: {model_name}")
    print(f"{'='*70}\n")
    
    start = time()
    model, tokenizer = load_model(model_name)
    
    for i, row in enumerate(releases, start=1):
        release = (row.get("tag_name") or row.get("name") or f"release_{i}").strip()
        desc = (row.get("name") or "").strip()
        
        print(f"[{i}/{len(releases)}] {release}...", end=" ", flush=True)
        
        try:
            prompt = build_prompt(prompt_template, release, desc, code)
            result = generate_response(model, tokenizer, prompt)
            append_csv(output_file, result, release, desc)
            print("✅")
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            append_csv(output_file, "", release, desc)
    
    del model, tokenizer
    torch.cuda.empty_cache()
    
    elapsed = time() - start
    print(f"\n✅ Concluído em {elapsed/60:.1f} minutos")
    print(f"📁 {output_file}\n")

# ============================================================================
# PASSO 6: DOWNLOAD DOS RESULTADOS
# ============================================================================

print(f"\n{'='*60}")
print("📥 DOWNLOAD DOS RESULTADOS")
print(f"{'='*60}\n")

for _, output_file in MODELOS:
    if os.path.exists(output_file):
        print(f"⬇️  Baixando {os.path.basename(output_file)}...")
        files.download(output_file)

print("\n✅ PROCESSAMENTO COMPLETO!")
print("✅ Todos os arquivos foram baixados!")
print(f"\n⏱️  Tempo total: {(time() - start)/60:.1f} minutos")
