import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import App from './App'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('mostra_versao_e_ambiente', async () => {
    const dados = { versao: '1.2.3', cor: 'azul', ambiente: 'producao' }
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(dados), { status: 200 })))
    render(<App />)
    expect(await screen.findByText('Versão 1.2.3 (producao)')).toBeTruthy()
  })

  it('mostra_mensagem_de_erro', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 503 })))
    render(<App />)
    expect(await screen.findByText('Falha ao consultar a versão: 503')).toBeTruthy()
  })
})
