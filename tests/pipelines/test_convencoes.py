"""Testes estruturais que valem para todo workflow do repositório."""
import re

import pytest

import workflows
from workflows import carregar_acao, carregar_workflow, jobs, listar_acoes, listar_workflows, passos, usos, usos_acao

NOMES = [p.name for p in listar_workflows()]

PADRAO_SHA = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
PADRAO_DOCKER = re.compile(r"^docker://[\w./-]+@sha256:[0-9a-f]{64}$")
EXCECAO_BIBLIOTECA = re.compile(r"^arkhibr/devops-fluxos-c3dm/.+@v1$")
NOME_VALIDO = re.compile(r"^(\d\d-[a-z0-9-]+\.yml|lib-[a-z0-9-]+\.yml|portal\.yml)$")
ESCRITAS = ("packages", "contents", "deployments")
GUARDAS = ("github.event_name != 'pull_request'", "github.ref == 'refs/heads/main'")


# Regras: cada função devolve a lista de violações de um workflow já carregado.

def violacoes_sha(wf, lista_usos=None):
    saida = []
    for uso in usos(wf) if lista_usos is None else lista_usos:
        if uso.startswith("./") or EXCECAO_BIBLIOTECA.match(uso) or PADRAO_DOCKER.match(uso):
            continue
        if not PADRAO_SHA.match(uso):
            saida.append(f"uses sem SHA de 40 caracteres: {uso}")
    return saida


def violacoes_permissions(wf):
    return [] if "permissions" in wf else ["falta permissions no topo"]


def _ligado(valor):
    """`continue-on-error` ligado: true, "true" ou qualquer expressão que não seja false."""
    if valor is True:
        return True
    if isinstance(valor, str):
        return valor.strip().lower() != "false"
    return False


def violacoes_continue_on_error(wf):
    saida = []
    for job in jobs(wf):
        lista = passos(wf, job)
        for i, passo in enumerate(lista):
            if not _ligado(passo.get("continue-on-error")):
                continue
            if "id" not in passo:
                saida.append(f"{job}: continue-on-error sem id")
                continue
            ref = f"steps.{passo['id']}.outcome"
            if not any(ref in str(p) for p in lista[i + 1:]):
                saida.append(f"{job}: nenhum passo posterior testa {ref}")
    return saida


def _eventos(wf):
    gatilhos = wf.get("on")
    if isinstance(gatilhos, (dict, list)):
        return set(gatilhos)
    return {gatilhos}


def violacoes_paths(wf, nome):
    proprio = f".github/workflows/{nome}"
    gatilhos = wf.get("on")
    if not isinstance(gatilhos, dict):
        return []
    return [
        f"paths de {evento} não inclui {proprio}"
        for evento, cfg in gatilhos.items()
        if isinstance(cfg, dict) and "paths" in cfg and proprio not in cfg["paths"]
    ]


def _escreve(permissions):
    if permissions == "write-all":
        return True
    return isinstance(permissions, dict) and any(permissions.get(k) == "write" for k in ESCRITAS)


def _guarda_valida(condicao):
    texto = str(condicao).strip()
    texto = re.sub(r"^\$\{\{\s*(.*?)\s*\}\}$", r"\1", texto)
    if "||" in texto:
        return False
    return any(parte.strip() in GUARDAS for parte in texto.split("&&"))


def violacoes_escrita_em_pr(wf):
    if "pull_request" not in _eventos(wf):
        return []
    topo = wf.get("permissions")
    return [
        f"{job}: escreve e pode rodar em pull_request sem guarda válida"
        for job, definicao in jobs(wf).items()
        if _escreve(definicao.get("permissions", topo)) and not _guarda_valida(definicao.get("if", ""))
    ]


def violacoes_concorrencia(wf):
    saida = []
    for job, definicao in jobs(wf).items():
        if "environment" not in definicao:
            continue
        conc = definicao.get("concurrency", wf.get("concurrency"))
        if not isinstance(conc, dict):
            saida.append(f"{job}: environment sem concurrency")
            continue
        if not str(conc.get("group", "")).startswith("implantacao-"):
            saida.append(f"{job}: grupo deve começar com implantacao-")
        if conc.get("cancel-in-progress") is not False:
            saida.append(f"{job}: cancel-in-progress deve ser false")
    return saida


# Testes sobre o repositório.

def test_carregar_normaliza_on(tmp_path, monkeypatch):
    (tmp_path / "x.yml").write_text("on: [push]\njobs: {}\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "PASTA_WORKFLOWS", tmp_path)
    wf = workflows.carregar_workflow("x.yml")
    assert wf["on"] == ["push"]
    assert True not in wf


def test_ha_ao_menos_um_workflow():
    assert "00-repositorio.yml" in NOMES


def test_nomes_de_arquivo_seguem_o_padrao():
    invalidos = [n for n in NOMES if not NOME_VALIDO.match(n)]
    assert not invalidos, f"nomes fora do padrão: {invalidos}"


@pytest.mark.parametrize("nome", NOMES)
def test_usos_fixados_por_sha(nome):
    assert not violacoes_sha(carregar_workflow(nome))


@pytest.mark.parametrize("caminho", listar_acoes(), ids=lambda c: c.parent.name)
def test_usos_das_composite_actions_fixados_por_sha(caminho):
    assert not violacoes_sha({}, usos_acao(carregar_acao(caminho)))


def test_composite_action_sem_sha_e_reprovada():
    acao = {"runs": {"using": "composite", "steps": [{"uses": "actions/checkout@v4"}, {"run": "echo"}]}}
    assert violacoes_sha({}, usos_acao(acao)) == ["uses sem SHA de 40 caracteres: actions/checkout@v4"]


@pytest.mark.parametrize("nome", NOMES)
def test_permissions_no_topo(nome):
    assert not violacoes_permissions(carregar_workflow(nome))


@pytest.mark.parametrize("nome", NOMES)
def test_continue_on_error_tem_verificacao(nome):
    assert not violacoes_continue_on_error(carregar_workflow(nome))


@pytest.mark.parametrize("nome", NOMES)
def test_paths_inclui_o_proprio_workflow(nome):
    assert not violacoes_paths(carregar_workflow(nome), nome)


@pytest.mark.parametrize("nome", NOMES)
def test_jobs_que_escrevem_nao_rodam_em_pull_request(nome):
    assert not violacoes_escrita_em_pr(carregar_workflow(nome))


@pytest.mark.parametrize("nome", NOMES)
def test_implantacoes_serializadas(nome):
    assert not violacoes_concorrencia(carregar_workflow(nome))


# Testes negativos permanentes: cada regra precisa reprovar um YAML mínimo que a viole.

def _carregar_texto(tmp_path, monkeypatch, texto):
    (tmp_path / "v.yml").write_text(texto, encoding="utf-8")
    monkeypatch.setattr(workflows, "PASTA_WORKFLOWS", tmp_path)
    return workflows.carregar_workflow("v.yml")


CASOS_VIOLACAO = {
    "sha": ("on: push\njobs:\n  a:\n    runs-on: x\n    steps:\n      - uses: actions/checkout@v4\n",
            lambda wf: violacoes_sha(wf)),
    "permissions": ("on: push\njobs: {}\n", lambda wf: violacoes_permissions(wf)),
    "continue-on-error": (
        "on: push\njobs:\n  a:\n    runs-on: x\n    steps:\n      - id: s\n        continue-on-error: true\n        run: x\n",
        lambda wf: violacoes_continue_on_error(wf)),
    "continue-on-error-string": (
        "on: push\njobs:\n  a:\n    runs-on: x\n    steps:\n      - continue-on-error: 'true'\n        run: x\n",
        lambda wf: violacoes_continue_on_error(wf)),
    "continue-on-error-expressao": (
        "on: push\njobs:\n  a:\n    runs-on: x\n    steps:\n      - id: s\n        continue-on-error: ${{ matrix.x }}\n        run: x\n",
        lambda wf: violacoes_continue_on_error(wf)),
    "paths": ("on:\n  push:\n    paths: ['src/**']\njobs: {}\n", lambda wf: violacoes_paths(wf, "v.yml")),
    "escrita-sem-guarda": (
        "on: pull_request\npermissions: {contents: read}\njobs:\n  a:\n    runs-on: x\n    permissions: {packages: write}\n    steps: []\n",
        lambda wf: violacoes_escrita_em_pr(wf)),
    "write-all-no-topo": (
        "on: pull_request\npermissions: write-all\njobs:\n  a:\n    runs-on: x\n    steps: []\n",
        lambda wf: violacoes_escrita_em_pr(wf)),
    "write-all-no-job": (
        "on: pull_request\npermissions: {}\njobs:\n  a:\n    runs-on: x\n    permissions: write-all\n    steps: []\n",
        lambda wf: violacoes_escrita_em_pr(wf)),
    "guarda-com-ou": (
        "on: pull_request\npermissions: {}\njobs:\n  a:\n    runs-on: x\n    permissions: {contents: write}\n"
        "    if: github.event_name != 'pull_request' || true\n    steps: []\n",
        lambda wf: violacoes_escrita_em_pr(wf)),
    "concorrencia-ausente": (
        "on: push\njobs:\n  a:\n    runs-on: x\n    environment: prod\n    steps: []\n",
        lambda wf: violacoes_concorrencia(wf)),
    "concorrencia-cancela": (
        "on: push\njobs:\n  a:\n    runs-on: x\n    environment: prod\n"
        "    concurrency: {group: implantacao-prod, cancel-in-progress: true}\n    steps: []\n",
        lambda wf: violacoes_concorrencia(wf)),
}


@pytest.mark.parametrize("caso", CASOS_VIOLACAO)
def test_regras_detectam_violacoes(caso, tmp_path, monkeypatch):
    texto, regra = CASOS_VIOLACAO[caso]
    assert regra(_carregar_texto(tmp_path, monkeypatch, texto)), f"regra não reprovou o caso {caso}"


GUARDAS_BOAS = [
    "github.event_name != 'pull_request'",
    "${{ github.event_name != 'pull_request' }}",
    "github.ref == 'refs/heads/main'",
    "github.ref == 'refs/heads/main' && needs.a.result == 'success'",
]


@pytest.mark.parametrize("guarda", GUARDAS_BOAS)
def test_guardas_validas_sao_aceitas(guarda, tmp_path, monkeypatch):
    texto = (
        "on: pull_request\npermissions: {}\njobs:\n  a:\n    runs-on: x\n    permissions: {packages: write}\n"
        f"    if: \"{guarda}\"\n    steps: []\n"
    )
    assert not violacoes_escrita_em_pr(_carregar_texto(tmp_path, monkeypatch, texto))


def test_yaml_vazio_nao_quebra(tmp_path, monkeypatch):
    wf = _carregar_texto(tmp_path, monkeypatch, "")
    assert wf == {}
    assert usos(wf) == []
    assert violacoes_permissions(wf)
    assert not violacoes_escrita_em_pr(wf)


def test_listar_inclui_yaml_e_ignora_arquivos_do_macos(tmp_path, monkeypatch):
    for nome in ("a.yml", "b.yaml", "._c.yml"):
        (tmp_path / nome).write_text("on: push\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "PASTA_WORKFLOWS", tmp_path)
    assert [p.name for p in workflows.listar_workflows()] == ["a.yml", "b.yaml"]
    assert not NOME_VALIDO.match("b.yaml")
