using OpalToolsSDK.Sample;
using Optimizely.Opal.Tools;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpalToolService();
builder.Services.AddOpalTool<GreetingTool>();
builder.Services.AddOpalTool<TodaysDateTool>();
builder.Services.AddOpalTool<AuthExampleTool>();

var app = builder.Build();

app.MapGet("/health", () => Results.Ok("Service is healthy"));
app.MapOpalTools();

app.Run();