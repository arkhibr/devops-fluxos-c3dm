"""Coleta dados pela API do GitHub e grava o relatório de métricas.

Uso: python3 coletar.py [--dias 30] [--repositorio dono/nome] [--saida metricas.md]

Exige a CLI `gh` autenticada. Todo acesso à rede fica neste arquivo. O cálculo está em `dora.py`.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dora  # noqa: E402


def chamar(caminho: str, **parametros: str) -> list[dict]:
    """Executa `gh api --paginate` e junta as páginas em uma lista."""
    comando = ["gh", "api", "--method", "GET", "--paginate", caminho]
    for chave, valor in parametros.items():
        comando += ["-f", f"{chave}={valor}"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        sys.exit(f"Falha em {' '.join(comando)}: {resultado.stderr.strip()}")
    saida = resultado.stdout
    decodificador, posicao, itens = json.JSONDecoder(), 0, []
    while posicao < len(saida):
        if saida[posicao].isspace():
            posicao += 1
            continue
        pagina, posicao = decodificador.raw_decode(saida, posicao)
        itens.extend(pagina["workflow_runs"] if isinstance(pagina, dict) and "workflow_runs" in pagina else pagina)
    return itens


def coletar_deployments(repo: str, desde: datetime) -> list[dict]:
    deployments = chamar(f"repos/{repo}/deployments", environment=dora.PRODUCAO, per_page="100")
    deployments = [d for d in deployments if datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")) >= desde]
    for deployment in deployments:
        statuses = chamar(f"repos/{repo}/deployments/{deployment['id']}/statuses", per_page="100")
        deployment["estado"] = dora.estado_final(statuses)
    return deployments


def coletar_prs(repo: str, desde: datetime) -> list[dict]:
    prs = chamar(f"repos/{repo}/pulls", state="closed", base="main", per_page="100")
    fundidos = [
        p for p in prs
        if p.get("merged_at") and datetime.fromisoformat(p["merged_at"].replace("Z", "+00:00")) >= desde
    ]
    for pr in fundidos:
        commits = chamar(f"repos/{repo}/pulls/{pr['number']}/commits", per_page="100")
        pr["primeiro_commit"] = min(c["commit"]["committer"]["date"] for c in commits) if commits else None
    return fundidos


def coletar_incidentes(repo: str, desde: datetime) -> list[dict]:
    issues = chamar(f"repos/{repo}/issues", state="all", labels="incidente", since=desde.strftime("%Y-%m-%dT%H:%M:%SZ"), per_page="100")
    return [
        i for i in issues
        if "pull_request" not in i and datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) >= desde
    ]


def coletar_execucoes(repo: str, desde: datetime) -> list[dict]:
    return chamar(f"repos/{repo}/actions/runs", created=f">={desde.strftime('%Y-%m-%d')}", per_page="100")


def formatar(valor: timedelta | None) -> str:
    """Escreve a duração em dias, horas, minutos e, abaixo de uma hora, segundos."""
    if valor is None:
        return "sem dados"
    segundos = round(valor.total_seconds())
    minutos, segundos = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    dias, horas = divmod(horas, 24)
    partes = [(dias, "d"), (horas, "h"), (minutos, "min")]
    if dias == 0 and horas == 0:
        partes.append((segundos, "s"))
    return " ".join(f"{n} {u}" for n, u in partes if n) or "0 s"


def decimal(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def montar_relatorio(repo: str, dias: int, deployments, prs, incidentes, runs) -> str:
    producao = [d for d in deployments if d.get("estado") in dora.ESTADOS_TERMINAIS]
    linhas = [
        f"# Métricas de entrega de {repo}",
        "",
        f"Janela de {dias} dias, encerrada em {datetime.now(timezone.utc):%d/%m/%Y}. "
        f"Base: {len(producao)} implantações de produção concluídas, {len(prs)} pull requests incorporados, "
        f"{len(incidentes)} incidentes e {len(runs)} execuções de workflow.",
        "",
        "| Métrica | Valor |",
        "| --- | --- |",
        f"| Frequência de implantação | {decimal(dora.frequencia_implantacao(deployments, dias))} por dia |",
        f"| Prazo de entrega de mudanças | {formatar(dora.prazo_entrega(prs, deployments))} |",
        f"| Taxa de falha de mudanças | {decimal(100 * dora.taxa_falha(deployments, incidentes), 1)}% |",
        f"| Tempo de recuperação de implantação com falha | {formatar(dora.tempo_restauracao(incidentes))} |",
        f"| Taxa de sucesso das execuções | {decimal(100 * dora.taxa_sucesso_execucoes(runs), 1)}% |",
        f"| Duração mediana das execuções | {formatar(dora.duracao_mediana(runs))} |",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("--dias", type=int, default=30)
    analisador.add_argument("--repositorio", default=os.environ.get("GITHUB_REPOSITORY"))
    analisador.add_argument("--saida", default="metricas.md")
    args = analisador.parse_args()
    repo = args.repositorio or subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], check=True, capture_output=True, text=True
    ).stdout.strip()
    desde = datetime.now(timezone.utc) - timedelta(days=args.dias)
    relatorio = montar_relatorio(
        repo, args.dias, coletar_deployments(repo, desde), coletar_prs(repo, desde), coletar_incidentes(repo, desde), coletar_execucoes(repo, desde)
    )
    Path(args.saida).write_text(relatorio, encoding="utf-8")
    if resumo := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(resumo, "a", encoding="utf-8") as arquivo:
            arquivo.write(relatorio)
    print(relatorio)


if __name__ == "__main__":
    main()
