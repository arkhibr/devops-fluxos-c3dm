"""Testes estruturais que valem para todo workflow do repositório."""
import re

import pytest

from workflows import carregar_workflow, jobs, listar_workflows, passos, usos

NOMES = [p.name for p in listar_workflows()]

PADRAO_SHA = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
PADRAO_DOCKER = re.compile(r"^docker://[\w./-]+@sha256:[0-9a-f]{64}$")
EXCECAO_BIBLIOTECA = re.compile(r"^arkhibr/devops-fluxos-c3dm/.+@v1$")
ESCRITAS = ("packages", "contents", "deployments")


def test_carregar_normaliza_on(tmp_path, monkeypatch):
    import workflows

    (tmp_path / "x.yml").write_text("on: [push]\njobs: {}\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "PASTA_WORKFLOWS", tmp_path)
    wf = workflows.carregar_workflow("x.yml")
    assert wf["on"] == ["push"]
    assert True not in wf


def test_ha_ao_menos_um_workflow():
    assert "00-repositorio.yml" in NOMES


@pytest.mark.parametrize("nome", NOMES)
def test_usos_fixados_por_sha(nome):
    for uso in usos(carregar_workflow(nome)):
        if uso.startswith("./"):
            continue
        if EXCECAO_BIBLIOTECA.match(uso) or PADRAO_DOCKER.match(uso):
            continue
        assert PADRAO_SHA.match(uso), f"{nome}: uses sem SHA de 40 caracteres: {uso}"


@pytest.mark.parametrize("nome", NOMES)
def test_permissions_no_topo(nome):
    assert "permissions" in carregar_workflow(nome), f"{nome}: falta permissions no topo"


@pytest.mark.parametrize("nome", NOMES)
def test_continue_on_error_tem_verificacao(nome):
    wf = carregar_workflow(nome)
    for job in jobs(wf):
        lista = passos(wf, job)
        for i, passo in enumerate(lista):
            if passo.get("continue-on-error") is not True:
                continue
            assert "id" in passo, f"{nome}/{job}: continue-on-error sem id"
            ref = f"steps.{passo['id']}.outcome"
            assert any(ref in str(p) for p in lista[i + 1:]), f"{nome}/{job}: nenhum passo testa {ref}"


def _paths_de(wf):
    gatilhos = wf.get("on")
    if not isinstance(gatilhos, dict):
        return []
    saida = []
    for evento, cfg in gatilhos.items():
        if isinstance(cfg, dict) and "paths" in cfg:
            saida.append((evento, cfg["paths"]))
    return saida


@pytest.mark.parametrize("nome", NOMES)
def test_paths_inclui_o_proprio_workflow(nome):
    proprio = f".github/workflows/{nome}"
    for evento, paths in _paths_de(carregar_workflow(nome)):
        assert proprio in paths, f"{nome}: paths de {evento} não inclui {proprio}"


def _eventos(wf):
    gatilhos = wf.get("on")
    if isinstance(gatilhos, dict):
        return set(gatilhos)
    if isinstance(gatilhos, list):
        return set(gatilhos)
    return {gatilhos}


def _escreve(permissions):
    return isinstance(permissions, dict) and any(permissions.get(k) == "write" for k in ESCRITAS)


@pytest.mark.parametrize("nome", NOMES)
def test_jobs_que_escrevem_nao_rodam_em_pull_request(nome):
    wf = carregar_workflow(nome)
    if "pull_request" not in _eventos(wf):
        return
    topo = wf.get("permissions")
    for job, definicao in jobs(wf).items():
        efetivas = definicao.get("permissions", topo)
        if not _escreve(efetivas):
            continue
        condicao = str(definicao.get("if", ""))
        assert "github.event_name != 'pull_request'" in condicao or "github.ref == 'refs/heads/main'" in condicao, (
            f"{nome}/{job}: escreve e pode rodar em pull_request sem condição"
        )


@pytest.mark.parametrize("nome", NOMES)
def test_implantacoes_serializadas(nome):
    wf = carregar_workflow(nome)
    for job, definicao in jobs(wf).items():
        if "environment" not in definicao:
            continue
        conc = definicao.get("concurrency", wf.get("concurrency"))
        assert isinstance(conc, dict), f"{nome}/{job}: environment sem concurrency"
        assert str(conc.get("group", "")).startswith("implantacao-"), f"{nome}/{job}: grupo deve começar com implantacao-"
        assert conc.get("cancel-in-progress") is False, f"{nome}/{job}: cancel-in-progress deve ser false"
