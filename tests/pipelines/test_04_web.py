"""Testes do cenário 04: CI da aplicação React."""
from workflows import carregar_workflow, passos

ARQUIVO = "04-web.yml"
JOB = "ci-web"


def _indice(comandos: list[str], fragmento: str) -> int:
    for posicao, comando in enumerate(comandos):
        if fragmento in comando:
            return posicao
    raise AssertionError(f"nenhum passo contém {fragmento}")


def test_04_ordem_dos_passos():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    textos = [p.get("run", "") + " " + p.get("uses", "") for p in lista]
    ordem = [
        _indice(textos, "npm ci"),
        _indice(textos, "npm run lint"),
        _indice(textos, "npm run typecheck"),
        _indice(textos, "npm test"),
        _indice(textos, "npm run build"),
        _indice(textos, "actions/upload-artifact"),
    ]
    assert ordem == sorted(ordem)
    assert len(set(ordem)) == len(ordem)


def test_04_usa_node_24_com_cache():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    node = [p for p in lista if "actions/setup-node" in p.get("uses", "")][0]["with"]
    assert str(node["node-version"]) == "24"
    assert node["cache"] == "npm"
    assert node["cache-dependency-path"] == "apps/web/package-lock.json"


def test_04_publica_dist_como_artefato():
    lista = passos(carregar_workflow(ARQUIVO), JOB)
    envio = [p for p in lista if "actions/upload-artifact" in p.get("uses", "")][0]["with"]
    assert envio["name"] == "web-dist"
    assert envio["path"] == "apps/web/dist"


def test_04_paths():
    wf = carregar_workflow(ARQUIVO)
    for evento in ("pull_request", "push"):
        caminhos = wf["on"][evento]["paths"]
        assert "apps/web/**" in caminhos
        assert f".github/workflows/{ARQUIVO}" in caminhos


def test_04_job_nao_colide_com_verificacoes_obrigatorias():
    wf = carregar_workflow(ARQUIVO)
    assert JOB in wf["jobs"]
    assert not {"build", "pytest", "actionlint", "titulo"} & set(wf["jobs"])
