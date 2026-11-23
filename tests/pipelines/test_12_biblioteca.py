"""Testes do cenário 12: biblioteca de workflows reutilizáveis e composite action."""
import re

import yaml

from workflows import PASTA_ACOES, PASTA_WORKFLOWS, RAIZ, carregar_acao, carregar_workflow, jobs, listar_workflows, passos

BIBLIOTECA = ["lib-dast.yml", "lib-dotnet-ci.yml", "lib-seguranca.yml", "lib-web-ci.yml"]
ACAO_REMOTA = "arkhibr/devops-fluxos-c3dm/.github/actions/resumo-falha@v1"


def _libs() -> list[str]:
    return [p.name for p in listar_workflows() if p.name.startswith("lib-")]


def _entradas(nome: str) -> dict:
    return carregar_workflow(nome)["on"]["workflow_call"]["inputs"]


def test_biblioteca_tem_os_quatro_workflows():
    assert _libs() == BIBLIOTECA


def test_lib_tem_workflow_call():
    for nome in _libs():
        assert "workflow_call" in carregar_workflow(nome)["on"], nome


def test_entradas_documentadas():
    for nome in _libs():
        for entrada, definicao in _entradas(nome).items():
            assert definicao.get("description", "").strip(), f"{nome}: entrada {entrada} sem description"
            assert definicao["type"] in {"string", "number", "boolean"}, f"{nome}: {entrada} sem type"


def test_interface_dotnet():
    e = _entradas("lib-dotnet-ci.yml")
    assert e["solucao"]["required"] is True and e["solucao"]["type"] == "string"
    assert e["dotnet-version"]["default"] == "10.0.x"
    assert e["cobertura-minima"]["type"] == "number" and e["cobertura-minima"]["default"] == 80
    assert e["diretorio"]["default"] == "."


def test_interface_web():
    e = _entradas("lib-web-ci.yml")
    assert e["diretorio"]["required"] is True
    assert str(e["node-version"]["default"]) == "24"


def test_interface_seguranca():
    e = _entradas("lib-seguranca.yml")
    assert e["linguagens"]["type"] == "string"
    assert e["config-gitleaks"]["default"] == ".gitleaks.toml"
    assert e["config-codeql"]["default"] == ""


def test_interface_dast():
    e = _entradas("lib-dast.yml")
    assert e["contexto-docker"]["required"] is True
    assert e["alvo"]["required"] is True
    assert e["porta"]["type"] == "number" and e["porta"]["default"] == 8080
    assert e["caminho-health"]["default"] == "/health"
    assert e["regras-zap"]["default"] == ""


def test_lib_termina_com_resumo_de_falha():
    for nome in _libs():
        wf = carregar_workflow(nome)
        for job in jobs(wf):
            ultimo = passos(wf, job)[-1]
            assert "failure()" in ultimo.get("if", ""), f"{nome}/{job}: último passo sem if failure()"
            assert ultimo["uses"] == ACAO_REMOTA, f"{nome}/{job}: último passo não chama resumo-falha"
            assert ultimo["with"]["etapa"], f"{nome}/{job}: etapa vazia"


def test_lib_faz_checkout_do_repositorio_chamador():
    for nome in _libs():
        wf = carregar_workflow(nome)
        for job in jobs(wf):
            checkout = [p for p in passos(wf, job) if p.get("uses", "").startswith("actions/checkout@")]
            assert checkout, f"{nome}/{job}: sem checkout"
            assert "repository" not in (checkout[0].get("with") or {}), f"{nome}/{job}: checkout de outro repositório"


def test_lib_nao_depende_de_arquivos_deste_repositorio():
    proibidos = ["apps/", ".zap/", "cenarios/", ".github/codeql", "./.github/actions", "devops-fluxos-c3dm/apps"]
    for nome in _libs():
        texto = (PASTA_WORKFLOWS / nome).read_text(encoding="utf-8")
        for trecho in proibidos:
            assert trecho not in texto, f"{nome} referencia {trecho}"
        assert ".gitleaks.toml" not in texto.replace("default: .gitleaks.toml", ""), nome


def test_lib_nao_exige_arquivos_opcionais_do_chamador():
    seguranca = (PASTA_WORKFLOWS / "lib-seguranca.yml").read_text(encoding="utf-8")
    assert '-f "$GITLEAKS_CONFIG"' in seguranca
    config_codeql = [
        p for p in passos(carregar_workflow("lib-seguranca.yml"), "codeql")
        if p.get("uses", "").startswith("github/codeql-action/init@")
    ][0]
    assert config_codeql["with"]["config-file"] == "${{ inputs.config-codeql }}"


def test_lib_seguranca_matriz_e_guarda_de_fork():
    job = carregar_workflow("lib-seguranca.yml")["jobs"]["codeql"]
    assert job["strategy"]["matrix"]["language"] == "${{ fromJSON(inputs.linguagens) }}"
    assert "head.repo.full_name == github.repository" in job["if"]
    assert job["permissions"]["security-events"] == "write"


def test_lib_dast_espera_health_com_limite():
    wf = carregar_workflow("lib-dast.yml")
    texto = "\n".join(p.get("run", "") for p in passos(wf, "zap"))
    assert "seq 1 60" in texto and "docker logs" in texto


def test_acao_resumo_falha():
    acao = carregar_acao(PASTA_ACOES / "resumo-falha" / "action.yml")
    assert acao["runs"]["using"] == "composite"
    assert acao["inputs"]["etapa"]["description"].strip()
    comandos = "\n".join(p.get("run", "") for p in acao["runs"]["steps"])
    assert "GITHUB_STEP_SUMMARY" in comandos
    assert "github.run_id" in yaml.safe_dump(acao)
    assert "github.job" in yaml.safe_dump(acao)
    assert all(p.get("shell") == "bash" for p in acao["runs"]["steps"] if "run" in p)


def test_cenarios_usam_biblioteca():
    for nome in ("03-api.yml", "04-web.yml", "06-seguranca.yml", "07-dast.yml"):
        wf = carregar_workflow(nome)
        usos = [j["uses"] for j in jobs(wf).values() if "uses" in j]
        assert any(u.startswith("./.github/workflows/lib-") for u in usos), nome


def test_chamadores_locais_apontam_para_arquivos_existentes():
    for nome in listar_workflows():
        for job in jobs(carregar_workflow(nome.name)).values():
            uso = job.get("uses", "")
            if uso.startswith("./"):
                assert (RAIZ / uso[2:]).is_file(), f"{nome.name}: {uso} não existe"


def test_readme_mostra_chamador_externo():
    texto = (RAIZ / "cenarios" / "12-biblioteca-reutilizavel" / "README.md").read_text(encoding="utf-8")
    for lib in BIBLIOTECA:
        assert re.search(rf"arkhibr/devops-fluxos-c3dm/\.github/workflows/{lib}@v1", texto), lib
