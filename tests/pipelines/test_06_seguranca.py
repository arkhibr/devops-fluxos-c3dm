"""Testes do cenário 06: SAST, SCA e varredura de segredos."""
import re
import tomllib

import yaml

from workflows import RAIZ, carregar_workflow, passos

ARQUIVO = "06-seguranca.yml"
FIXTURES = "cenarios/06-seguranca-estatica/fixtures"
PADRAO_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _passo(job: str, id_: str) -> dict:
    return [p for p in passos(carregar_workflow(ARQUIVO), job) if p.get("id") == id_][0]


def test_gitleaks_ignora_somente_fixtures():
    config = tomllib.loads((RAIZ / ".gitleaks.toml").read_text(encoding="utf-8"))
    assert config["extend"]["useDefault"] is True
    assert config["allowlists"] == [
        {
            "description": "Fixtures do cenário 06, que devem ser reprovados pela varredura de segredos",
            "paths": [f"^{FIXTURES}/"],
        },
        {
            "description": "Falso positivo: nome da imagem no teste do cenário 08",
            "condition": "AND",
            "targetRules": ["generic-api-key"],
            "paths": [r"^tests/pipelines/test_08_artefato\.py$"],
            "regexes": ["devops-fluxos-c3dm-(api|web)"],
        },
    ]


def test_fixtures_verificam_outcome():
    wf = carregar_workflow(ARQUIVO)
    lista = passos(wf, "fixtures-devem-reprovar")
    final = lista[-1]
    texto = yaml.safe_dump(final)
    for id_ in ("semgrep", "gitleaks", "osv"):
        assert f"steps.{id_}.outcome" in texto
        passo = _passo("fixtures-devem-reprovar", id_)
        assert passo["continue-on-error"] is True
        assert lista.index(passo) < lista.index(final)
    assert "failure" in final["run"]
    assert "exit" in final["run"]


def test_fixtures_exigem_o_achado_esperado_e_nao_so_a_falha():
    final = passos(carregar_workflow(ARQUIVO), "fixtures-devem-reprovar")[-1]["run"]
    assert "csharp-sqli" in final
    assert "generic-api-key" in final
    assert "lodash" in final


def test_fixtures_usam_as_ferramentas_esperadas():
    semgrep = _passo("fixtures-devem-reprovar", "semgrep")["run"]
    gitleaks = _passo("fixtures-devem-reprovar", "gitleaks")["run"]
    osv = _passo("fixtures-devem-reprovar", "osv")["run"]
    assert "--config p/csharp" in semgrep and "--error" in semgrep
    assert "--no-git" in gitleaks and "--config" not in gitleaks
    assert "package-lock.json:$FIXTURES/lockfile-vulneravel.json" in osv
    assert not (RAIZ / FIXTURES / "package-lock.json").exists()
    lock = (RAIZ / FIXTURES / "lockfile-vulneravel.json").read_text(encoding="utf-8")
    assert '"version": "4.17.15"' in lock


def test_codeql_matriz():
    wf = carregar_workflow(ARQUIVO)
    job = wf["jobs"]["codeql"]
    assert job["strategy"]["matrix"]["language"] == ["csharp", "javascript-typescript"]
    assert job["permissions"]["security-events"] == "write"
    assert "head.repo.full_name == github.repository" in job["if"]
    assert wf["permissions"] == {"contents": "read"}
    init = [p for p in job["steps"] if p.get("uses", "").startswith("github/codeql-action/init@")][0]
    assert init["with"]["build-mode"] == "none"
    assert init["with"]["config-file"] == "./.github/codeql/codeql-config.yml"


def test_codeql_ignora_fixtures():
    config = yaml.safe_load((RAIZ / ".github" / "codeql" / "codeql-config.yml").read_text(encoding="utf-8"))
    assert config["paths-ignore"] == ["cenarios/06-seguranca-estatica/fixtures/**"]


def test_dependencias_somente_em_pull_request():
    job = carregar_workflow(ARQUIVO)["jobs"]["dependencias"]
    assert job["if"] == "github.event_name == 'pull_request'"
    revisao = [p for p in job["steps"] if "dependency-review-action" in p.get("uses", "")][0]
    assert revisao["with"]["fail-on-severity"] == "high"
    assert "allow-ghsas" not in revisao["with"]


def test_segredos_usa_cli_com_checksum():
    wf = carregar_workflow(ARQUIVO)
    job = wf["jobs"]["segredos"]
    assert PADRAO_SHA256.match(job["env"]["GITLEAKS_SHA256"])
    texto = yaml.safe_dump(job["steps"])
    assert "sha256sum -c" in texto
    assert "gitleaks detect --source . --config .gitleaks.toml --redact --exit-code 1" in texto
    assert not any("gitleaks/gitleaks-action" in p.get("uses", "") for p in job["steps"])
    assert job["steps"][0]["with"]["fetch-depth"] == 0


def test_ferramentas_da_esteira_com_versao_e_checksum_fixados():
    env = carregar_workflow(ARQUIVO)["jobs"]["fixtures-devem-reprovar"]["env"]
    assert PADRAO_SHA256.match(env["GITLEAKS_SHA256"])
    assert PADRAO_SHA256.match(env["OSV_SHA256"])
    assert re.match(r"^\d+\.\d+\.\d+$", env["SEMGREP_VERSION"])


def test_jobs_nao_colidem_com_verificacoes_obrigatorias():
    nomes = set(carregar_workflow(ARQUIVO)["jobs"])
    assert nomes == {"codeql", "dependencias", "segredos", "fixtures-devem-reprovar"}
    assert not {"build", "pytest", "actionlint", "titulo"} & nomes


def test_fixtures_existem_com_o_conteudo_esperado():
    pasta = RAIZ / FIXTURES
    assert "SELECT" in (pasta / "Consulta.cs").read_text(encoding="utf-8")
    token = re.search(r"^API_TOKEN=(\S+)$", (pasta / "config.env").read_text(encoding="utf-8"), re.M)
    assert token and len(token.group(1)) == 40
    assert not re.match(r"^(ghp_|gho_|ghs_|github_pat_|AKIA|ASIA|sk-|xox|AIza|glpat-)", token.group(1))
