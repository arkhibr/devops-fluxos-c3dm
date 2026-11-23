#!/usr/bin/env bash
# Regrava o upstream ponderado do roteador a partir do modelo e recarrega o NGINX.
# Uso: ajustar-pesos.sh <atributo-estavel> <atributo-canario>
# Cada atributo é `weight=N` ou `fora`, que apaga o destino do upstream. Exemplos:
#   ajustar-pesos.sh weight=9 weight=1   envia 10% das requisições ao canário
#   ajustar-pesos.sh fora weight=1       promove o canário a 100%
#   ajustar-pesos.sh weight=1 fora       remove o canário
# O arquivo é copiado com `docker cp`, sem montagem de volume.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Uso: $0 <weight=N|fora> <weight=N|fora>" >&2
  exit 2
fi
for atributo in "$1" "$2"; do
  if ! [[ "$atributo" =~ ^(weight=[1-9][0-9]*|fora)$ ]]; then
    echo "Atributo inválido: ${atributo}" >&2
    exit 2
  fi
done

pasta="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
temporario="$(mktemp)"
trap 'rm -f "$temporario"' EXIT

if [ "$1" = "fora" ] && [ "$2" = "fora" ]; then
  echo "Ao menos um destino deve permanecer no upstream." >&2
  exit 2
fi

# Um destino apagado do upstream deixa de ser resolvido pelo NGINX, o que permite
# remover um canário cujo contêiner já foi parado.
sed -e "s/^\\( *server estavel:8080\\) ESTAVEL /\\1 $1 /" -e "s/^\\( *server canario:8080\\) CANARIO /\\1 $2 /" \
  -e "/server estavel:8080 fora /d" -e "/server canario:8080 fora /d" \
  "${pasta}/nginx.conf.tmpl" > "$temporario"
docker cp "$temporario" roteador:/etc/nginx/conf.d/default.conf
docker exec roteador nginx -t
docker exec roteador nginx -s reload
echo "Roteador ajustado: estavel ${1}, canario ${2}."
