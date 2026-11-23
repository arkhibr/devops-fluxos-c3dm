"""Testes do cenário 05: teste e lint da própria esteira."""
import re
import shutil
import subprocess

import pytest
import yaml

from workflows import PASTA_WORKFLOWS, RAIZ, carregar_workflow, passos

ARQUIVO = "05-esteira.yml"
JOB = "detecta-erro"
EXEMPLO = RAIZ / "cenarios" / "05-teste-da-esteira" / "exemplos" / "workflow-com-erro.yml"
PADRAO_IMAGEM = re.compile(r"rhysd/actionlint@sha256:[0-9a-f]{64}")


def _imagem_actionlint() -> str:
    texto = (PASTA_WORKFLOWS / "00-repositorio.yml").read_text(encoding="utf-8")
    return PADRAO_IMAGEM.search(texto).group(0)


def _docker_disponivel() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def test_05_exemplo_tem_erro_esperado():
    """O exemplo precisa reprovar no actionlint, com os dois erros documentados."""
    if not _docker_disponivel():
        pytest.skip("Docker indisponível")
    # O conteúdo entra por stdin porque bind mounts do Colima chegam vazios.
    resultado = subprocess.run(
        ["docker", "run", "--rm", "-i", _imagem_actionlint(), "-"],
        input=EXEMPLO.read_bytes(), capture_output=True, timeout=300,
    )
    saida = (resultado.stdout + resultado.stderr).decode("utf-8")
    assert resultado.returncode != 0, saida
    assert "refx" in saida
    assert "runs-on" in saida


def test_05_exemplo_e_yaml_valido_fora_da_pasta_de_workflows():
    assert yaml.safe_load(EXEMPLO.read_text(encoding="utf-8"))
    assert PASTA_WORKFLOWS not in EXEMPLO.parents


def test_05_exemplo_contem_os_dois_erros():
    texto = EXEMPLO.read_text(encoding="utf-8")
    assert "github.refx" in texto
    assert "runs-on" not in texto


def test_05_job_nao_colide_com_verificacoes_obrigatorias():
    wf = carregar_workflow(ARQUIVO)
    assert JOB in wf["jobs"]
    assert not {"build", "pytest", "actionlint", "titulo"} & set(wf["jobs"])


def test_05_passo_do_lint_tolera_falha_e_o_seguinte_exige_falha():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    lint = [p for p in lista if p.get("id") == "lint-exemplo"][0]
    assert lint["continue-on-error"] is True
    posterior = lista[lista.index(lint) + 1]
    assert "steps.lint-exemplo.outcome != 'failure'" in posterior["if"]
    assert "exit 1" in posterior["run"]


def test_05_usa_a_mesma_imagem_do_actionlint_do_repositorio():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    lint = [p for p in lista if p.get("id") == "lint-exemplo"][0]
    assert _imagem_actionlint() in lint["run"]
    assert "workflow-com-erro.yml" in lint["run"]


def test_05_paths():
    wf = carregar_workflow(ARQUIVO)
    for evento in ("pull_request", "push"):
        caminhos = wf["on"][evento]["paths"]
        assert "cenarios/05-teste-da-esteira/**" in caminhos
        assert f".github/workflows/{ARQUIVO}" in caminhos


def test_05_workflow_exige_os_dois_erros_esperados_na_saida():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    lint = [p for p in lista if p.get("id") == "lint-exemplo"][0]
    assert "actionlint-exemplo.txt" in lint["run"]
    verificacao = lista[-1]
    assert "steps.lint-exemplo.outcome == 'failure'" in verificacao["if"]
    assert "grep -q 'refx'" in verificacao["run"]
    assert "grep -q 'runs-on'" in verificacao["run"]


def test_05_readme_usa_o_digest_fixado():
    texto = (RAIZ / "cenarios" / "05-teste-da-esteira" / "README.md").read_text(encoding="utf-8")
    assert _imagem_actionlint() in texto
    assert "actionlint:latest" not in texto
