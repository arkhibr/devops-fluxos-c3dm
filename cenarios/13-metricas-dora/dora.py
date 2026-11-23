"""Funções puras que calculam as métricas DORA e de esteira.

Os argumentos são listas de dicionários no formato da API REST do GitHub, com dois
acréscimos feitos por `coletar.py`: cada deployment traz a chave `estado`, que resume
o último status terminal, e cada pull request traz a chave `primeiro_commit`, com a
data do commit mais antigo. Nenhuma função faz acesso à rede.
"""
from datetime import datetime, timedelta
from statistics import median

PRODUCAO = "producao"
ESTADOS_TERMINAIS = ("success", "failure", "error")
CONCLUSOES_CONTADAS = ("success", "failure", "timed_out")


def _data(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def _mediana(duracoes: list[timedelta]) -> timedelta | None:
    if not duracoes:
        return None
    return timedelta(seconds=median(d.total_seconds() for d in duracoes))


def estado_final(statuses: list[dict]) -> str | None:
    """Devolve o estado terminal mais recente de um deployment.

    A API lista os statuses do mais novo para o mais antigo. Os estados `inactive`,
    `in_progress` e `queued` não dizem se a implantação deu certo, e `inactive` é
    gravado pelo GitHub quando um deployment posterior o substitui.
    """
    for status in statuses:
        if status.get("state") in ESTADOS_TERMINAIS:
            return status["state"]
    return None


def _producao(deployments: list[dict], estados: tuple[str, ...] = ESTADOS_TERMINAIS) -> list[dict]:
    selecionados = [d for d in deployments if d.get("environment") == PRODUCAO and d.get("estado") in estados]
    return sorted(selecionados, key=lambda d: _data(d["created_at"]))


def frequencia_implantacao(deployments: list[dict], dias: int) -> float:
    """Implantações de produção com êxito por dia."""
    if dias <= 0:
        return 0.0
    return len(_producao(deployments, ("success",))) / dias


def prazo_entrega(prs: list[dict], deployments: list[dict]) -> timedelta | None:
    """Mediana entre o primeiro commit de cada pull request e a produção.

    A produção é o primeiro deployment bem-sucedido cujo `sha` é o merge commit ou
    cuja criação é posterior ao merge. A ordem temporal substitui a verificação de
    ancestralidade, porque o deployment dos cenários disparados por `workflow_run`
    registra o HEAD da branch principal, e não o commit da imagem.
    """
    sucessos = _producao(deployments, ("success",))
    prazos = []
    for pr in prs:
        if not pr.get("merged_at") or not pr.get("primeiro_commit"):
            continue
        fusao = _data(pr["merged_at"])
        implantacao = next(
            (d for d in sucessos if d["sha"] == pr.get("merge_commit_sha") or _data(d["created_at"]) >= fusao),
            None,
        )
        if implantacao is not None:
            prazos.append(_data(implantacao["created_at"]) - _data(pr["primeiro_commit"]))
    return _mediana(prazos)


def taxa_falha(deployments: list[dict], incidentes: list[dict]) -> float:
    """Fração de implantações de produção com falha ou seguidas de incidente.

    Um incidente é atribuído ao último deployment de produção criado antes dele, de
    modo que cobre o intervalo até o próximo deployment. Cada deployment conta uma vez.
    """
    todos = _producao(deployments)
    if not todos:
        return 0.0
    com_falha = {d["id"] for d in todos if d["estado"] != "success"}
    for incidente in incidentes:
        abertura = _data(incidente["created_at"])
        anteriores = [d for d in todos if _data(d["created_at"]) <= abertura]
        if anteriores:
            com_falha.add(anteriores[-1]["id"])
    return len(com_falha) / len(todos)


def tempo_restauracao(incidentes: list[dict]) -> timedelta | None:
    """Mediana de `closed_at - created_at` dos incidentes fechados."""
    return _mediana([_data(i["closed_at"]) - _data(i["created_at"]) for i in incidentes if i.get("closed_at")])


def _concluidas(runs: list[dict]) -> list[dict]:
    return [r for r in runs if r.get("status") == "completed" and r.get("conclusion") in CONCLUSOES_CONTADAS]


def taxa_sucesso_execucoes(runs: list[dict]) -> float:
    """Execuções com êxito sobre as concluídas, sem contar canceladas nem em andamento."""
    concluidas = _concluidas(runs)
    if not concluidas:
        return 0.0
    return sum(1 for r in concluidas if r["conclusion"] == "success") / len(concluidas)


def duracao_mediana(runs: list[dict]) -> timedelta | None:
    """Mediana de `updated_at - run_started_at` das execuções concluídas."""
    return _mediana([_data(r["updated_at"]) - _data(r["run_started_at"]) for r in _concluidas(runs)])
