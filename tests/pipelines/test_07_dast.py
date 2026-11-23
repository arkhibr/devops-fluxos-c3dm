"""Testes do cenário 07: DAST com OWASP ZAP baseline."""
import re

import yaml

from workflows import RAIZ, carregar_workflow, passos

ARQUIVO = "07-dast.yml"
LIB = "lib-dast.yml"


def _passo_zap(job: str, arquivo: str = ARQUIVO) -> dict:
    return [p for p in passos(carregar_workflow(arquivo), job) if "zaproxy/action-baseline" in p.get("uses", "")][0]


def test_07_chama_a_biblioteca():
    chamada = carregar_workflow(ARQUIVO)["jobs"]["zap-api"]
    assert chamada["uses"] == f"./.github/workflows/{LIB}"
    assert chamada["with"] == {
        "contexto-docker": "apps/api",
        "porta": 8080,
        "caminho-health": "/health",
        "alvo": "http://localhost:8080/api/v1/versao",
        "regras-zap": ".zap/regras.tsv",
    }


def test_07_espera_health():
    lista = passos(carregar_workflow(LIB), "zap")
    run = "\n".join(p.get("run", "") for p in lista)
    assert "docker build" in run and "${PORTA}" in run
    assert "${CAMINHO}" in run
    assert "seq 1 60" in run or "-lt 60" in run
    assert "docker logs" in run
    ordem = [i for i, p in enumerate(lista) if "CAMINHO" in p.get("run", "")]
    zap = [i for i, p in enumerate(lista) if "zaproxy" in p.get("uses", "")]
    assert ordem[0] < zap[0]


def test_07_fail_action():
    zap = _passo_zap("zap", LIB)
    assert re.match(r"^zaproxy/action-baseline@[0-9a-f]{40}$", zap["uses"])
    assert zap["with"]["target"] == "${{ inputs.alvo }}"
    assert zap["with"]["rules_file_name"] == "${{ steps.regras.outputs.arquivo }}"
    assert zap["with"]["fail_action"] is True
    assert zap["with"]["allow_issue_writing"] is False
    assert "continue-on-error" not in zap


def test_regras_tem_justificativa():
    linhas = (RAIZ / ".zap" / "regras.tsv").read_text(encoding="utf-8").splitlines()
    for linha in linhas:
        if not linha.strip() or linha.startswith("#"):
            continue
        campos = linha.split("\t")
        assert len(campos) >= 3 and campos[2].strip(), f"regra sem justificativa: {linha!r}"
        assert campos[1] in {"IGNORE", "INFO", "WARN", "FAIL", "OUTOFSCOPE"}


def test_fixture_deve_reprovar_pelo_motivo_esperado():
    wf = carregar_workflow(ARQUIVO)
    lista = passos(wf, "fixture-deve-reprovar")
    zap = _passo_zap("fixture-deve-reprovar")
    assert zap["id"] == "zap-fixture" and zap["continue-on-error"] is True
    assert zap["with"]["fail_action"] is True and zap["with"]["allow_issue_writing"] is False
    assert zap["with"]["artifact_name"] != _passo_zap("zap", LIB)["with"]["artifact_name"]
    final = lista[-1]
    assert lista.index(zap) < lista.index(final)
    assert "steps.zap-fixture.outcome" in yaml.safe_dump(final)
    assert "failure" in final["run"] and "exit" in final["run"]
    assert "10021" in final["run"] and "pluginid" in final["run"]


def test_fixture_usa_nginx_sem_cabecalhos():
    pasta = RAIZ / "cenarios" / "07-seguranca-dinamica" / "fixtures"
    conf = (pasta / "nginx-sem-cabecalhos.conf").read_text(encoding="utf-8")
    assert "add_header" not in conf.replace("# add_header", "")
    assert (pasta / "index.html").exists()


def test_permissoes_e_nomes():
    wf = carregar_workflow(ARQUIVO)
    assert wf["permissions"] == {"contents": "read"}
    assert set(wf["jobs"]) == {"zap-api", "fixture-deve-reprovar"}
    caminhos = wf["on"]["pull_request"]["paths"]
    assert ".github/workflows/07-dast.yml" in caminhos
