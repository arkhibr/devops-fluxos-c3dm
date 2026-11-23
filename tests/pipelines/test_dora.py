"""Testes das métricas DORA e de esteira do cenário 13."""
import importlib.util
import json
from datetime import timedelta

import pytest

from workflows import RAIZ, carregar_workflow

CAMINHO = RAIZ / "cenarios" / "13-metricas-dora" / "dora.py"
especificacao = importlib.util.spec_from_file_location("dora", CAMINHO)
dora = importlib.util.module_from_spec(especificacao)
especificacao.loader.exec_module(dora)

DADOS = RAIZ / "tests" / "pipelines" / "dados"


def _ler(nome: str) -> list[dict]:
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def test_frequencia_esperada():
    assert dora.frequencia_implantacao(_ler("deployments.json"), dias=10) == pytest.approx(0.5)


def test_frequencia_ignora_homologacao_e_falhas():
    deployments = _ler("deployments.json")
    producao_ok = [d for d in deployments if d["environment"] == "producao" and d["estado"] == "success"]
    assert len(producao_ok) == 5
    assert len(deployments) == 7


def test_prazo_entrega_mediana():
    # PR 1: 49h, PR 2: 25h, PR 3: 13h, PR 4: 73h (pula o deployment com falha). Mediana de 13, 25, 49, 73.
    assert dora.prazo_entrega(_ler("prs.json"), _ler("deployments.json")) == timedelta(hours=37)


def test_prazo_entrega_sem_deployment_posterior_e_none():
    prs = [{"merge_commit_sha": "zzz", "merged_at": "2026-12-01T00:00:00Z", "primeiro_commit": "2026-11-30T00:00:00Z"}]
    assert dora.prazo_entrega(prs, _ler("deployments.json")) is None


def test_taxa_falha_conta_status_e_incidente():
    # 1 deployment com failure e 1 sucesso seguido de incidente, em 6 deployments de produção.
    assert dora.taxa_falha(_ler("deployments.json"), _ler("issues.json")) == pytest.approx(1 / 3)


def test_incidente_sobre_deployment_com_falha_nao_conta_duas_vezes():
    incidente = [{"created_at": "2026-11-05T12:00:00Z", "closed_at": None}]
    assert dora.taxa_falha(_ler("deployments.json"), incidente) == pytest.approx(1 / 6)


def test_restauracao_mediana():
    assert dora.tempo_restauracao(_ler("issues.json")) == timedelta(hours=3)


def test_restauracao_sem_incidentes_e_none():
    assert dora.tempo_restauracao([]) is None
    assert dora.tempo_restauracao([{"created_at": "2026-11-07T11:00:00Z", "closed_at": None}]) is None


def test_listas_vazias_nao_dividem_por_zero():
    assert dora.frequencia_implantacao([], dias=10) == 0.0
    assert dora.taxa_falha([], []) == 0.0
    assert dora.frequencia_implantacao(_ler("deployments.json"), dias=0) == 0.0
    assert dora.taxa_sucesso_execucoes([]) == 0.0
    assert dora.duracao_mediana([]) is None
    assert dora.prazo_entrega([], []) is None


def test_taxa_sucesso_ignora_cancelada_e_em_andamento():
    assert dora.taxa_sucesso_execucoes(_ler("runs.json")) == pytest.approx(0.75)


def test_duracao_mediana_das_execucoes_concluidas():
    assert dora.duracao_mediana(_ler("runs.json")) == timedelta(minutes=5)


@pytest.mark.parametrize(
    "statuses, esperado",
    [
        ([{"state": "inactive"}, {"state": "success"}, {"state": "in_progress"}], "success"),
        ([{"state": "failure"}, {"state": "in_progress"}], "failure"),
        ([{"state": "in_progress"}, {"state": "queued"}], None),
        ([], None),
    ],
)
def test_estado_final_ignora_inactive_e_intermediarios(statuses, esperado):
    assert dora.estado_final(statuses) == esperado


def test_workflow_13_agenda_e_permissoes():
    wf = carregar_workflow("13-metricas.yml")
    assert wf["on"]["schedule"] == [{"cron": "0 9 * * 1"}]
    assert "workflow_dispatch" in wf["on"]
    assert wf["permissions"] == {
        "contents": "read",
        "deployments": "read",
        "issues": "read",
        "actions": "read",
        "pull-requests": "read",
    }
