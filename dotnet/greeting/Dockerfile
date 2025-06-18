FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /source

# Copy source code
COPY ./ ./

# Build the sample
RUN dotnet publish ./OpalToolsSDK.Sample.csproj -c Release -o /app

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "OpalToolsSDK.Sample.dll"]

# Expose port 80
EXPOSE 80
ENV ASPNETCORE_URLS=http://+:80