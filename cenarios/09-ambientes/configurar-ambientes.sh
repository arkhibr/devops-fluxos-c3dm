#!/usr/bin/env bash
# Cria os ambientes homologacao e producao no repositório informado, grava a
# variável APP_ENV em cada um e gera o segredo TOKEN_DEMONSTRACAO sem exibi-lo.
# Cada ambiente aceita implantação somente a partir do ramo main. Idempotente.
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
  # Política de ramos personalizada: só ramos com política cadastrada podem implantar.
  printf '%s' '{"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}' \
    | gh api --method PUT "repos/${repositorio}/environments/${ambiente}" --input - --silent
  existentes="$(gh api "repos/${repositorio}/environments/${ambiente}/deployment-branch-policies" --jq '.branch_policies[].name')"
  if ! grep -qx 'main' <<<"$existentes"; then
    gh api --method POST "repos/${repositorio}/environments/${ambiente}/deployment-branch-policies" \
      -f name=main -f type=branch --silent
  fi
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
