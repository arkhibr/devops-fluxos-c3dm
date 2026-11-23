namespace Api;

/// <summary>Acrescenta a toda resposta os cabeçalhos exigidos pelo ZAP baseline.</summary>
public sealed class CabecalhosSeguranca(RequestDelegate proximo)
{
    public Task InvokeAsync(HttpContext contexto)
    {
        contexto.Response.OnStarting(() =>
        {
            var cabecalhos = contexto.Response.Headers;
            cabecalhos["X-Content-Type-Options"] = "nosniff";
            cabecalhos["X-Frame-Options"] = "DENY";
            cabecalhos["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'";
            cabecalhos["Referrer-Policy"] = "no-referrer";
            cabecalhos["Cross-Origin-Resource-Policy"] = "same-origin";
            cabecalhos["Cache-Control"] = "no-store";
            return Task.CompletedTask;
        });
        return proximo(contexto);
    }
}
