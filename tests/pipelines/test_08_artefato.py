"""Testes do cenário 08: imagem construída uma vez e promovida por tag."""
import re

from workflows import carregar_workflow, passos

ARQUIVO = "08-artefato.yml"
IMAGENS = ("devops-fluxos-c3dm-api", "devops-fluxos-c3dm-web")


def _texto(job: str) -> str:
    return "\n".join(str(p) for p in passos(carregar_workflow(ARQUIVO), job))


def test_promover_nao_reconstroi():
    wf = carregar_workflow(ARQUIVO)
    lista = passos(wf, "promover")
    run = "\n".join(p.get("run", "") for p in lista)
    assert not re.search(r"docker build(?!x imagetools)", run)
    assert not any("build-push-action" in p.get("uses", "") for p in lista)
    assert "docker buildx imagetools create" in run


def test_promover_valida_entradas_por_env():
    wf = carregar_workflow(ARQUIVO)
    lista = passos(wf, "promover")
    for passo in lista:
        assert "${{ inputs." not in passo.get("run", ""), "entrada interpolada direto no script"
    validacao = [p for p in lista if "[0-9a-f]{7,40}" in p.get("run", "")]
    assert validacao and "inputs.sha" in str(validacao[0].get("env", {}))
    entradas = wf["on"]["workflow_dispatch"]["inputs"]
    assert entradas["ambiente"]["type"] == "choice"
    assert entradas["ambiente"]["options"] == ["homologacao", "producao"]
    assert entradas["sha"]["required"] is True


def test_publicacao_so_fora_de_pr():
    wf = carregar_workflow(ARQUIVO)
    for job in ("publicar", "promover"):
        definicao = wf["jobs"][job]
        assert definicao["permissions"]["packages"] == "write"
        assert "github.ref == 'refs/heads/main'" in definicao["if"]
        assert "||" not in definicao["if"]
    assert wf["permissions"] == {"contents": "read"}
    validar = wf["jobs"]["validar-imagem"]
    assert "packages" not in validar.get("permissions", {})
    assert not any("login-action" in p.get("uses", "") for p in passos(wf, "validar-imagem"))
    for passo in passos(wf, "validar-imagem"):
        if "build-push-action" in passo.get("uses", ""):
            assert passo["with"]["push"] is False


def test_tag_por_sha():
    wf = carregar_workflow(ARQUIVO)
    texto = _texto("publicar")
    assert "type=sha,prefix=sha-,format=short" in texto
    assert "ghcr.io/arkhibr/" in yaml_env(wf) or "ghcr.io/arkhibr/" in texto
    assert "latest" not in texto
    push = [p for p in passos(wf, "publicar") if "build-push-action" in p.get("uses", "")][0]
    assert push["with"]["push"] is True
    assert "org.opencontainers.image.source=https://github.com/arkhibr/devops-fluxos-c3dm" in push["with"]["labels"]
    assert re.search(r"login-action@[0-9a-f]{40}", _texto("publicar"))


def yaml_env(wf: dict) -> str:
    return str(wf.get("env", ""))


def test_nomes_das_imagens_e_paths():
    wf = carregar_workflow(ARQUIVO)
    texto = str(wf)
    for imagem in IMAGENS:
        assert f"ghcr.io/arkhibr/{imagem}" in texto or imagem.rsplit("-", 1)[1] in texto
    assert set(wf["jobs"]) == {"validar-imagem", "publicar", "promover"}
    for evento in ("pull_request", "push"):
        assert ".github/workflows/08-artefato.yml" in wf["on"][evento]["paths"]
    assert wf["on"]["push"]["branches"] == ["main"]
