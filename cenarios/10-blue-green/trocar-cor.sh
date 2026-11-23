#!/usr/bin/env bash
# Aponta o roteador para a cor informada: gera a configuração a partir do
# modelo, copia para o contêiner `roteador`, valida e recarrega o NGINX.
# O arquivo é copiado com `docker cp`, sem montagem de volume, de modo que o
# script funciona também em máquinas cujo Docker não enxerga o diretório do repositório.
set -euo pipefail

cor="${1:-}"
if [ "$cor" != "blue" ] && [ "$cor" != "green" ]; then
  echo "Uso: $0 <blue|green>" >&2
  exit 2
fi

pasta="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
temporario="$(mktemp)"
trap 'rm -f "$temporario"' EXIT

sed "s/COR_ATIVA/${cor}/" "${pasta}/nginx.conf.tmpl" > "$temporario"
docker cp "$temporario" roteador:/etc/nginx/conf.d/default.conf
docker exec roteador nginx -t
docker exec roteador nginx -s reload
echo "Roteador apontado para ${cor}."
