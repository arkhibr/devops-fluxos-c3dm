"""Testes do portal MkDocs: cada cenário tem página e entrada no nav, com as seções fixadas."""
import re
from pathlib import Path

import pytest
import yaml

from workflows import RAIZ

SECOES = [
    "## Problema que a prática resolve",
    "## Workflow do cenário",
    "## Como executar",
    "## Como levar a prática a um sistema existente",
    "## Nível C3DM e fontes",
]
READMES = sorted((RAIZ / "cenarios").glob("*/README.md"))


class LeitorMkdocs(yaml.SafeLoader):
    """Loader que ignora tags como `!!python/name:` usadas pelo tema Material."""


LeitorMkdocs.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)
LeitorMkdocs.add_multi_constructor("!", lambda loader, suffix, node: None)


def carregar_mkdocs() -> dict:
    with open(RAIZ / "mkdocs.yml", encoding="utf-8") as arquivo:
        return yaml.load(arquivo, Loader=LeitorMkdocs)


def arquivos_do_nav(item) -> list[str]:
    if isinstance(item, str):
        return [item]
    if isinstance(item, list):
        return [a for sub in item for a in arquivos_do_nav(sub)]
    if isinstance(item, dict):
        return [a for sub in item.values() for a in arquivos_do_nav(sub)]
    return []


def test_mkdocs_tem_configuracao_basica():
    config = carregar_mkdocs()
    assert config["site_name"] == "Fluxos de CI/CD pelo modelo C3DM"
    assert config["theme"]["name"] == "material"
    assert config["theme"]["language"] == "pt-BR"
    assert "superpowers/" in config["exclude_docs"]


def test_nav_aponta_para_arquivos_existentes():
    nav = carregar_mkdocs()["nav"]
    ausentes = [a for a in arquivos_do_nav(nav) if not (RAIZ / "docs" / a).is_file()]
    assert not ausentes, f"entradas do nav sem arquivo em docs/: {ausentes}"


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.parent.name)
def test_todo_cenario_tem_pagina_e_entrada_no_nav(readme: Path):
    pasta = readme.parent.name
    numero = pasta.split("-")[0]
    pagina = RAIZ / "docs" / "cenarios" / f"{numero}.md"
    assert pagina.is_file(), f"falta docs/cenarios/{numero}.md"
    esperado = f'{{% include-markdown "../../cenarios/{pasta}/README.md" %}}'
    assert pagina.read_text(encoding="utf-8").strip() == esperado
    assert f"cenarios/{numero}.md" in arquivos_do_nav(carregar_mkdocs()["nav"])


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.parent.name)
def test_readme_de_cenario_tem_secoes_obrigatorias(readme: Path):
    encontradas = re.findall(r"^## .+$", readme.read_text(encoding="utf-8"), flags=re.M)
    assert encontradas == SECOES
