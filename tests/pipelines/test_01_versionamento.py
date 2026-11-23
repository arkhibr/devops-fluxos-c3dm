"""Testes do cenário 01: títulos convencionais, release-please e tag móvel de versão maior."""
import json

from workflows import RAIZ, carregar_workflow, passos

TIPOS = {"feat", "fix", "docs", "chore", "ci", "test", "refactor"}


def test_titulo_pr_valida_tipos():
    wf = carregar_workflow("01-titulo-pr.yml")
    passo = next(p for p in passos(wf, "titulo") if "amannn/action-semantic-pull-request" in p.get("uses", ""))
    assert set(passo["with"]["types"].split()) == TIPOS
    assert wf["permissions"] == {"pull-requests": "read"}


def test_release_please_pacote_unico():
    config = json.loads((RAIZ / "release-please-config.json").read_text(encoding="utf-8"))
    assert list(config["packages"]) == ["."]
    assert config["packages"]["."]["release-type"] == "simple"
    assert "release-as" not in config["packages"]["."]
    assert config["include-v-in-tag"] is True
    manifesto = json.loads((RAIZ / ".release-please-manifest.json").read_text(encoding="utf-8"))
    assert manifesto == {".": "1.0.0"}


def test_release_roda_somente_em_push_na_main():
    wf = carregar_workflow("01-release.yml")
    assert set(wf["on"]) == {"push"}
    assert wf["on"]["push"]["branches"] == ["main"]
    assert {"contents": "write", "pull-requests": "write", "issues": "write", "actions": "write"} == wf["permissions"]
    comandos = "\n".join(p.get("run", "") for p in passos(wf, "release-please"))
    assert "gh workflow run 01-tag-principal.yml" in comandos
    guarda = next(p for p in passos(wf, "release-please") if "gh workflow run" in p.get("run", ""))["if"]
    assert "release_created" in guarda


def test_tag_principal_dispara_em_release():
    wf = carregar_workflow("01-tag-principal.yml")
    assert wf["on"]["release"]["types"] == ["published"]
    assert "workflow_dispatch" in wf["on"]
    assert wf["permissions"] == {"contents": "write"}
    comandos = "\n".join(p.get("run", "") for p in passos(wf, "tag-principal"))
    assert "GITHUB_REF_NAME%%.*" in comandos
    assert comandos.index('git tag -f "$principal"') < comandos.index('git push -f origin "refs/tags/$principal"')
    assert "=~ ^v[0-9]+\\." in comandos and "exit 1" in comandos
