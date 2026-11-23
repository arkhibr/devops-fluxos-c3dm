using Api;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.UseMiddleware<CabecalhosSeguranca>();

app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));

app.MapGet("/api/v1/versao", (IConfiguration configuracao) => Results.Ok(new
{
    versao = configuracao["APP_VERSION"] ?? "dev",
    cor = configuracao["APP_COLOR"] ?? "nenhuma",
    ambiente = configuracao["APP_ENV"] ?? "local",
}));

app.Run();

public partial class Program { }
