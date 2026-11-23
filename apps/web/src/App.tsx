import { useEffect, useState } from 'react'
import { buscarVersao } from './versao'

export default function App() {
  const [texto, setTexto] = useState('Consultando a versão...')

  useEffect(() => {
    buscarVersao()
      .then((v) => setTexto(`Versão ${v.versao} (${v.ambiente})`))
      .catch((e: Error) => setTexto(e.message))
  }, [])

  return (
    <main>
      <h1>Aplicação de exemplo</h1>
      <p>{texto}</p>
    </main>
  )
}
