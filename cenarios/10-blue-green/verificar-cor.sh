#!/usr/bin/env bash
# Consulta /api/v1/versao na porta informada, com até 30 tentativas de 2 segundos,
# e confere se a cor e a versão da resposta são as esperadas.
# Uso: verificar-cor.sh <porta> <cor> <versao>
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Uso: $0 <porta> <cor> <versao>" >&2
  exit 2
fi
porta="$1"
cor_esperada="$2"
versao_esperada="$3"

resposta=""
for _ in $(seq 1 30); do
  if resposta=$(curl -fsS --max-time 5 "http://127.0.0.1:${porta}/api/v1/versao" 2>/dev/null) \
    && [ "$(jq -r .cor <<< "$resposta")" = "$cor_esperada" ] \
    && [ "$(jq -r .versao <<< "$resposta")" = "$versao_esperada" ]; then
    echo "Porta ${porta}: ${resposta}"
    exit 0
  fi
  sleep 2
done
echo "::error::Porta ${porta}: esperado cor=${cor_esperada} e versao=${versao_esperada}, recebido: ${resposta:-sem resposta}"
exit 1
