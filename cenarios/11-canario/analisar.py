#!/usr/bin/env python3
"""Analisa a amostra de requisições de um lançamento canário.

A entrada é a saída de um laço de `curl`, com uma linha por requisição: a cor
informada pela API (`canario` ou `estavel`) ou a palavra `erro` quando a
requisição falhou.
"""
import argparse
import json
import sys

COR_CANARIO = "canario"
LINHA_ERRO = "erro"


def analisar(cores: list[str], erros: int, peso_esperado: float, tolerancia: float) -> dict:
    """Reprova sem amostras, com qualquer erro ou com proporção fora da tolerância."""
    if not cores:
        return {"proporcao_canario": 0.0, "aprovado": False, "motivo": "sem amostras para analisar"}
    proporcao = cores.count(COR_CANARIO) / len(cores)
    if erros > 0:
        return {
            "proporcao_canario": proporcao,
            "aprovado": False,
            "motivo": f"{erros} erro(s) nas requisições, e qualquer erro reprova o canário",
        }
    desvio = abs(proporcao - peso_esperado)
    if desvio > tolerancia:
        return {
            "proporcao_canario": proporcao,
            "aprovado": False,
            "motivo": (
                f"proporção do canário {proporcao:.3f} fora do intervalo "
                f"{peso_esperado:.3f} ± {tolerancia:.3f}"
            ),
        }
    return {
        "proporcao_canario": proporcao,
        "aprovado": True,
        "motivo": f"proporção do canário {proporcao:.3f} dentro de {peso_esperado:.3f} ± {tolerancia:.3f} e sem erros",
    }


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--peso", type=float, required=True, help="proporção esperada do canário, entre 0 e 1")
    parser.add_argument("--tolerancia", type=float, required=True, help="desvio máximo aceito em relação ao peso")
    args = parser.parse_args(argumentos)

    linhas = [linha.strip() for linha in sys.stdin if linha.strip()]
    erros = sum(1 for linha in linhas if linha == LINHA_ERRO)
    cores = [linha for linha in linhas if linha != LINHA_ERRO]
    resultado = analisar(cores, erros, args.peso, args.tolerancia)
    print(json.dumps(resultado, ensure_ascii=False))
    return 0 if resultado["aprovado"] else 1


if __name__ == "__main__":
    sys.exit(main())
