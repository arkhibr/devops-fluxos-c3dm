using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Api.Tests;

public class EndpointsTests
{
    private static WebApplicationFactory<Program> CriarFabrica(
        string? versao = null, string? cor = null, string? ambiente = null) =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(b =>
        {
            if (versao is not null) b.UseSetting("APP_VERSION", versao);
            if (cor is not null) b.UseSetting("APP_COLOR", cor);
            if (ambiente is not null) b.UseSetting("APP_ENV", ambiente);
        });

    [Fact]
    public async Task Health_retorna_healthy()
    {
        using var fabrica = CriarFabrica();
        var resposta = await fabrica.CreateClient().GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, resposta.StatusCode);
        var corpo = await resposta.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("healthy", corpo.GetProperty("status").GetString());
    }

    [Fact]
    public async Task Versao_usa_variaveis_de_ambiente()
    {
        using var fabrica = CriarFabrica("1.2.3", "green", "homologacao");
        var resposta = await fabrica.CreateClient().GetAsync("/api/v1/versao");

        Assert.Equal(HttpStatusCode.OK, resposta.StatusCode);
        var corpo = await resposta.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("1.2.3", corpo.GetProperty("versao").GetString());
        Assert.Equal("green", corpo.GetProperty("cor").GetString());
        Assert.Equal("homologacao", corpo.GetProperty("ambiente").GetString());
    }

    [Fact]
    public async Task Versao_sem_variaveis_usa_padroes()
    {
        using var fabrica = CriarFabrica();
        var corpo = await fabrica.CreateClient().GetFromJsonAsync<JsonElement>("/api/v1/versao");

        Assert.Equal("dev", corpo.GetProperty("versao").GetString());
        Assert.Equal("nenhuma", corpo.GetProperty("cor").GetString());
        Assert.Equal("local", corpo.GetProperty("ambiente").GetString());
    }

    [Fact]
    public async Task Respostas_trazem_cabecalhos_de_seguranca()
    {
        using var fabrica = CriarFabrica();
        var resposta = await fabrica.CreateClient().GetAsync("/health");

        Assert.Equal("nosniff", resposta.Headers.GetValues("X-Content-Type-Options").Single());
        Assert.Equal("DENY", resposta.Headers.GetValues("X-Frame-Options").Single());
        Assert.Equal("default-src 'none'; frame-ancestors 'none'",
            resposta.Headers.GetValues("Content-Security-Policy").Single());
        Assert.Equal("no-referrer", resposta.Headers.GetValues("Referrer-Policy").Single());
        Assert.Equal("same-origin", resposta.Headers.GetValues("Cross-Origin-Resource-Policy").Single());
        Assert.Equal("no-store", resposta.Headers.GetValues("Cache-Control").Single());
    }
}
