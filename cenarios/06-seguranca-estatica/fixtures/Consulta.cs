using System.Data.SqlClient;

namespace Fixtures;

// Exemplo didático com falha de injeção de SQL. Não faz parte da aplicação.
public class Consulta
{
    public SqlDataReader BuscarCliente(SqlConnection conexao, string nome)
    {
        var comando = new SqlCommand(
            "SELECT * FROM Clientes WHERE Nome = '" + nome + "'", conexao);
        return comando.ExecuteReader();
    }
}
