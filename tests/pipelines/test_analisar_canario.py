"""Testes da análise de proporção e de erros do cenário 11."""
import importlib.util
import subprocess
import sys

from workflows import RAIZ

CAMINHO = RAIZ / "cenarios" / "11-canario" / "analisar.py"
especificacao = importlib.util.spec_from_file_location("analisar_canario", CAMINHO)
modulo = importlib.util.module_from_spec(especificacao)
especificacao.loader.exec_module(modulo)
analisar = modulo.analisar


def _cores(canario: int, total: int) -> list[str]:
    return ["canario"] * canario + ["estavel"] * (total - canario)


def test_proporcao_dentro_da_tolerancia_aprova():
    r = analisar(_cores(20, 200), erros=0, peso_esperado=0.10, tolerancia=0.06)
    assert r["aprovado"] is True
    assert r["proporcao_canario"] == 0.10


def test_proporcao_fora_reprova():
    r = analisar(_cores(60, 200), erros=0, peso_esperado=0.10, tolerancia=0.06)
    assert r["aprovado"] is False
    assert "proporção" in r["motivo"]


def test_qualquer_erro_reprova():
    r = analisar(_cores(20, 200), erros=1, peso_esperado=0.10, tolerancia=0.06)
    assert r["aprovado"] is False
    assert "erro" in r["motivo"]


def test_lista_vazia_reprova():
    r = analisar([], erros=0, peso_esperado=0.10, tolerancia=0.06)
    assert r["aprovado"] is False
    assert "sem amostras" in r["motivo"]


def _executar(entrada: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CAMINHO), "--peso", "0.10", "--tolerancia", "0.06", *args],
        input=entrada, capture_output=True, text=True, check=False,
    )


def test_main_aprova_com_saida_do_laco():
    entrada = "canario\n" + "estavel\n" * 9
    assert _executar(entrada * 20).returncode == 0


def test_main_reprova_com_linha_de_erro():
    entrada = ("canario\n" + "estavel\n" * 9) * 20 + "erro\n"
    resultado = _executar(entrada)
    assert resultado.returncode == 1
    assert "erro" in resultado.stdout
