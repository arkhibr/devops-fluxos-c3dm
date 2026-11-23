#!/usr/bin/env bash
# Cria os ambientes homologacao e producao no repositório informado, grava a
# variável APP_ENV em cada um e gera o segredo TOKEN_DEMONSTRACAO sem exibi-lo.
# Uso: configurar-ambientes.sh <dono>/<repositorio>
set -euo pipefail

repositorio="${1:-}"
if ! [[ "$repositorio" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "Uso: $0 <dono>/<repositorio>" >&2
  exit 2
fi

for ambiente in homologacao producao; do
  echo "Configurando o ambiente ${ambiente}"
  # Sem revisores obrigatórios: a promoção para produção depende só do job anterior.
  gh api --method PUT "repos/${repositorio}/environments/${ambiente}" --silent
  gh variable set APP_ENV --env "$ambiente" --repo "$repositorio" --body "$ambiente"
  # O valor segue por entrada padrão para não aparecer na lista de processos nem no terminal.
  openssl rand -hex 20 | gh secret set TOKEN_DEMONSTRACAO --env "$ambiente" --repo "$repositorio"
done

echo "Ambientes configurados. Variáveis e segredos por ambiente:"
for ambiente in homologacao producao; do
  echo "- ${ambiente}"
  gh variable list --env "$ambiente" --repo "$repositorio"
  gh secret list --env "$ambiente" --repo "$repositorio"
done
