export interface Versao {
  versao: string
  cor: string
  ambiente: string
}

export async function buscarVersao(fetcher: typeof fetch = fetch): Promise<Versao> {
  const resposta = await fetcher('/api/v1/versao')
  if (!resposta.ok) {
    throw new Error(`Falha ao consultar a versão: ${resposta.status}`)
  }
  return (await resposta.json()) as Versao
}
