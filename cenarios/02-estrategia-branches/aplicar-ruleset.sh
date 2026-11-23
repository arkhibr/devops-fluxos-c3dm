#!/usr/bin/env bash
# Aplica o ruleset versionado em ruleset-main.json ao repositório informado.
# Uso: aplicar-ruleset.sh <dono>/<repositorio>
# Idempotente: se já existir um ruleset com o mesmo nome, ele é atualizado (PUT).
# Requer o GitHub CLI (gh) autenticado com permissão de administração e o jq instalado.
set -euo pipefail

repo="${1:?Uso: $0 <dono>/<repositorio>}"
pasta="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
arquivo="${pasta}/ruleset-main.json"
nome="$(jq -r '.name' "${arquivo}")"

id="$(gh api --paginate "repos/${repo}/rulesets" | jq -r --arg nome "${nome}" '.[] | select(.name == $nome) | .id' | head -n 1)"

if [ -n "${id}" ]; then
  echo "Atualizando o ruleset ${nome} (id ${id}) em ${repo}"
  gh api --method PUT "repos/${repo}/rulesets/${id}" --input "${arquivo}" --silent
else
  echo "Criando o ruleset ${nome} em ${repo}"
  gh api --method POST "repos/${repo}/rulesets" --input "${arquivo}" --silent
fi

gh api "repos/${repo}/rulesets" --jq '.[] | "\(.id)\t\(.name)\t\(.enforcement)"'
