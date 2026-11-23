"""Testes dos cenários 10 e 11: implantação blue-green e canário."""
import os

from workflows import RAIZ, carregar_workflow, jobs, passos

ARQ_10 = "10-blue-green.yml"
ARQ_11 = "11-canario.yml"


def _passos_job(arquivo: str, job: str = "implantar") -> list[dict]:
    return passos(carregar_workflow(arquivo), job)


def _indice(lista: list[dict], trecho: str) -> int:
    for i, passo in enumerate(lista):
        if trecho in passo.get("run", ""):
            return i
    raise AssertionError(f"nenhum passo contém {trecho!r}")


def _entradas_validadas(arquivo: str, *entradas: str) -> None:
    wf = carregar_workflow(arquivo)
    validacao = [p for p in passos(wf, "preparar") if "[0-9a-f]{7,40}" in p.get("run", "")]
    assert validacao
    for entrada in entradas:
        assert f"inputs.{entrada}" in str(validacao[0]["env"])
    assert "docker buildx imagetools inspect" in "\n".join(p.get("run", "") for p in passos(wf, "preparar"))


def _sem_interpolacao_em_run(arquivo: str) -> None:
    wf = carregar_workflow(arquivo)
    for nome in jobs(wf):
        for passo in passos(wf, nome):
            assert "${{" not in passo.get("run", ""), f"{nome}: expressão interpolada em run"


def test_10_tem_reversao_em_falha():
    wf = carregar_workflow(ARQ_10)
    lista = _passos_job(ARQ_10)
    troca = _indice(lista, "trocar-cor.sh green")
    reversao = next(i for i, p in enumerate(lista) if p.get("if") == "failure()")
    assert "trocar-cor.sh blue" in lista[reversao]["run"]
    assert reversao > troca
    assert lista[reversao]["if"] == "failure()"
    assert "verificar-cor.sh 8081 blue" in lista[reversao]["run"]
    limpeza = lista[-1]
    assert limpeza["if"] == "always()" and "down -v" in limpeza["run"]
    assert wf["jobs"]["implantar"]["environment"] == "producao"
    assert wf["jobs"]["implantar"]["concurrency"] == {"group": "implantacao-producao", "cancel-in-progress": False}


def test_10_verifica_a_cor_direta_antes_de_trocar():
    lista = _passos_job(ARQ_10)
    direta = _indice(lista, "verificar-cor.sh 8092 green")
    assert direta < _indice(lista, "trocar-cor.sh green")
    assert _indice(lista, "verificar-cor.sh 8081 green") > _indice(lista, "trocar-cor.sh green")


def test_10_gatilho_permissoes_e_entradas():
    wf = carregar_workflow(ARQ_10)
    assert set(wf["on"]) == {"workflow_dispatch"}
    entradas = wf["on"]["workflow_dispatch"]["inputs"]
    assert entradas["sha"]["required"] is True
    assert entradas["sha_anterior"]["required"] is False
    assert entradas["simular_falha"]["type"] == "boolean"
    assert wf["permissions"] == {"contents": "read", "packages": "read"}
    assert wf["jobs"]["implantar"]["needs"] == "preparar"
    _entradas_validadas(ARQ_10, "sha", "sha_anterior")
    _sem_interpolacao_em_run(ARQ_10)


def test_10_arquivos_de_apoio():
    pasta = RAIZ / "cenarios" / "10-blue-green"
    assert os.access(pasta / "trocar-cor.sh", os.X_OK)
    assert os.access(pasta / "verificar-cor.sh", os.X_OK)
    compose = (pasta / "compose.yml").read_text(encoding="utf-8")
    assert "container_name: roteador" in compose
    assert ":?" in compose
    assert "COR_ATIVA" in (pasta / "nginx.conf.tmpl").read_text(encoding="utf-8")
