"""Testes do cenário 09: ambientes com variáveis e segredos."""
import re

from workflows import carregar_workflow, jobs, passos

ARQUIVO = "09-ambientes.yml"
AMBIENTES = ("homologacao", "producao")


def _run(job: str) -> str:
    return "\n".join(p.get("run", "") for p in passos(carregar_workflow(ARQUIVO), job))


def test_09_producao_depende_de_homologacao():
    wf = carregar_workflow(ARQUIVO)
    assert set(jobs(wf)) == {"preparar", *AMBIENTES}
    assert "homologacao" in wf["jobs"]["producao"]["needs"]
    assert wf["jobs"]["homologacao"]["needs"] == "preparar"
    for nome in AMBIENTES:
        assert wf["jobs"][nome]["environment"] == nome
        assert wf["jobs"][nome]["concurrency"] == {
            "group": f"implantacao-{nome}",
            "cancel-in-progress": False,
        }


def test_09_segredo_nao_aparece_em_echo():
    wf = carregar_workflow(ARQUIVO)
    for nome in jobs(wf):
        for passo in passos(wf, nome):
            assert "secrets." not in passo.get("run", ""), f"{nome}: segredo interpolado em run"
            assert "${{" not in passo.get("run", ""), f"{nome}: expressão interpolada em run"
            for linha in passo.get("run", "").splitlines():
                assert not (re.search(r"\becho\b", linha) and "TOKEN_DEMONSTRACAO" in linha)
    for nome in AMBIENTES:
        env = "".join(str(p.get("env", "")) for p in passos(wf, nome))
        assert "secrets.TOKEN_DEMONSTRACAO" in env


def test_09_smoke_confere_ambiente():
    wf = carregar_workflow(ARQUIVO)
    for nome in AMBIENTES:
        lista = passos(wf, nome)
        smoke = [p for p in lista if "/api/v1/versao" in p.get("run", "")]
        assert smoke, f"{nome}: sem teste de fumaça"
        assert "vars.APP_ENV" in str(smoke[0]["env"])
        assert ".ambiente" in smoke[0]["run"] and ".versao" in smoke[0]["run"]
        assert "docker compose" in smoke[0]["run"] and "logs" in smoke[0]["run"]
        limpeza = lista[-1]
        assert limpeza["if"] == "always()" and "docker compose" in limpeza["run"] and "down -v" in limpeza["run"]


def test_09_gatilhos_e_permissoes():
    wf = carregar_workflow(ARQUIVO)
    assert wf["permissions"] == {"contents": "read", "packages": "read"}
    assert wf["on"]["workflow_run"]["workflows"] == ["08 Artefato único"]
    assert wf["on"]["workflow_run"]["branches"] == ["main"]
    assert wf["on"]["workflow_dispatch"]["inputs"]["sha"]["required"] is True
    guarda = wf["jobs"]["preparar"]["if"]
    assert "workflow_run.conclusion == 'success'" in guarda
    assert "pull_request" not in wf["on"]


def test_09_entradas_validadas_por_env():
    wf = carregar_workflow(ARQUIVO)
    validacao = [p for p in passos(wf, "preparar") if "[0-9a-f]{7,40}" in p.get("run", "")]
    assert validacao and "inputs.sha" in str(validacao[0]["env"])
    assert "docker buildx imagetools inspect" in _run("preparar")
