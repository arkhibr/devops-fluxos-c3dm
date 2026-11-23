"""Utilitários para ler e inspecionar os workflows do repositório."""
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2]
PASTA_WORKFLOWS = RAIZ / ".github" / "workflows"


def listar_workflows() -> list[Path]:
    """Lista os arquivos de workflow, sem subpastas, em ordem alfabética."""
    arquivos = [*PASTA_WORKFLOWS.glob("*.yml"), *PASTA_WORKFLOWS.glob("*.yaml")]
    return sorted(a for a in arquivos if not a.name.startswith("._"))


def carregar_workflow(nome: str) -> dict:
    """Lê o YAML e normaliza a chave `on`, que o PyYAML interpreta como True."""
    with open(PASTA_WORKFLOWS / nome, encoding="utf-8") as arquivo:
        wf = yaml.safe_load(arquivo) or {}
    if True in wf:
        wf["on"] = wf.pop(True)
    return wf


def jobs(wf: dict) -> dict[str, dict]:
    return wf.get("jobs") or {}


def passos(wf: dict, job: str) -> list[dict]:
    return jobs(wf)[job].get("steps") or []


def usos(wf: dict) -> list[str]:
    """Todos os `uses:` de jobs (workflows reutilizáveis) e de passos."""
    encontrados = []
    for nome, definicao in jobs(wf).items():
        if "uses" in definicao:
            encontrados.append(definicao["uses"])
        for passo in passos(wf, nome):
            if "uses" in passo:
                encontrados.append(passo["uses"])
    return encontrados
