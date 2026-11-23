"""Testes do cenário 02: ruleset versionado do ramo principal e script de aplicação."""
import json
import re

from workflows import RAIZ, carregar_workflow, jobs, listar_workflows

PASTA = RAIZ / "cenarios" / "02-estrategia-branches"


def carregar_ruleset() -> dict:
    return json.loads((PASTA / "ruleset-main.json").read_text(encoding="utf-8"))


def regras_por_tipo() -> dict[str, dict]:
    return {regra["type"]: regra for regra in carregar_ruleset()["rules"]}


def test_ruleset_tem_regras_obrigatorias():
    ruleset = carregar_ruleset()
    assert ruleset["target"] == "branch"
    assert ruleset["enforcement"] == "active"
    assert ruleset["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    regras = regras_por_tipo()
    assert {"deletion", "non_fast_forward", "required_linear_history", "pull_request", "required_status_checks"} <= set(regras)
    revisao = regras["pull_request"]["parameters"]
    assert revisao["required_approving_review_count"] == 0
    assert revisao["dismiss_stale_reviews_on_push"] is True


def test_ruleset_nao_tem_regra_de_tag():
    # O 01-tag-principal move a tag móvel v1 com force-push, o que uma regra de tag bloquearia.
    assert carregar_ruleset()["target"] != "tag"
    assert not [r for r in carregar_ruleset()["rules"] if "tag" in r["type"]]


def test_administrador_do_repositorio_contorna_o_ruleset():
    # O pull request de release usa GITHUB_TOKEN e não dispara as verificações obrigatórias.
    atores = carregar_ruleset()["bypass_actors"]
    assert {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"} in atores


def nomes_de_jobs() -> set[str]:
    nomes = set()
    for arquivo in listar_workflows():
        for id_job, definicao in jobs(carregar_workflow(arquivo.name)).items():
            nomes.add(definicao.get("name", id_job))
    return nomes


def test_status_checks_existem():
    exigidos = {c["context"] for c in regras_por_tipo()["required_status_checks"]["parameters"]["required_status_checks"]}
    assert {"pytest", "actionlint", "build"} <= exigidos
    assert exigidos <= nomes_de_jobs()


def test_script_usa_gh_api():
    script = (PASTA / "aplicar-ruleset.sh").read_text(encoding="utf-8")
    assert "gh api" in script
    assert "/rulesets" in script
    assert "--method PUT" in script
    assert not re.search(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|Bearer\s+[A-Za-z0-9]", script)
