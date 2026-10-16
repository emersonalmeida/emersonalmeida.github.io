#!/usr/bin/env python3
"""Script extração rápida de DOCX sem importar docx em execute_code."""

import subprocess
import glob

docx_files = [
    "docs/conversas-ia-blog-historico-pesquisa.docx",
    "docs/historico-design-2026-vagas-globais.docx", 
    "docs/historico_product_design_discovery_workshops.docx",
    "docs/negocios-necessidades-historico.docx"
]

for dpath in docx_files:
    try:
        with open(dpath, 'rb') as f:
            # DOCX é umZIP — tenta extrair texto de todos os xml .rels ou par/word dentro
            # Fallback simples: leia o arquivo como binário e extraia strings legíveis via regex ou grep interno
            content = f.read()
            
        # Tenta converter com antepenúltimas linhas do arquivo (ou extrai texto cru se possível)
        # Usa um commando python local que usa o site-packages
        print(f"[{dpath.split('/')[-1]}] Tentando extração rápida...")
    except Exception as e:
        print(f"[{dpath}] Erro na leitura bruta: {e}")

# Para DOCX, uso uma abordagem direta via subprocesso com um script Python que usa o python-docx já instalado ou disponível globalmente
print("\n=== TENTATIVA VIA SUBPROCESSO ===\n")

for dfile in ["conversas-ia-blog-historico-pesquisa.docx", "historico-design-2026-vagas-globais.docx", 
               "historico_product_design_discovery_workshops.docx", "negocios-necessidades-historico.docx"]:
    dpath = f"/home/ea/github/emersonalmeida.github.io/docs/{dfile}"
    
    # Escreve um mini script local que lê o docx sem importar em execute_code
    import_site_pkgs_script = """
import sys

doc_path = sys.argv[1]
try:
    from docx import Document
except ImportError:
    print(f"[{doc_path.split('/')[-1]}] IMPORTERRO — installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "-q"], check=False)
    from docx import Document

print(f"[{doc_path.split('/')[-1]}] OK — document loaded.")
doc = Document(doc_path)

lines = []
for p in doc.paragraphs:
    text = p.text.strip()
    if text:
        lines.append(text)

# Limita a primeiros e últimos elementos para mostrar o "antes-depois" de cada documento
print(f"[{doc_path.split('/')[-1]}] Preview:")
total_lines = len(lines)
head_lines = lines[:8]
tail_lines = lines[-8:] if total_lines > 20 else lines

# Mostra os primeiros e últimos blocos com delimitador
for label in ["Head ({len=head_lines)} linhas):", " ...":]:
    # Separa head/tail
    pass

