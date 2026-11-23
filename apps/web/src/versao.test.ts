import { describe, expect, it, vi } from 'vitest'
import { buscarVersao } from './versao'

function resposta(status: number, corpo: unknown): typeof fetch {
  return vi.fn(async () => new Response(JSON.stringify(corpo), { status })) as unknown as typeof fetch
}

describe('buscarVersao', () => {
  it('retorna_dados_quando_200', async () => {
    const dados = { versao: '1.2.3', cor: 'azul', ambiente: 'producao' }
    const fetcher = resposta(200, dados)
    await expect(buscarVersao(fetcher)).resolves.toEqual(dados)
    expect(fetcher).toHaveBeenCalledWith('/api/v1/versao')
  })

  it('lanca_erro_quando_500', async () => {
    await expect(buscarVersao(resposta(500, {}))).rejects.toThrow('Falha ao consultar a versão: 500')
  })
})
