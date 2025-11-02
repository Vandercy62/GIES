Write-Host "🔍 Testando login no ERP Primotex..." -ForegroundColor Yellow

$uri = "http://127.0.0.1:8002/api/v1/auth/login"
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    Write-Host "📡 Fazendo requisição para: $uri" -ForegroundColor Cyan
    
    $response = Invoke-WebRequest -Uri $uri -Method POST -Body $body -Headers $headers -TimeoutSec 15
    
    Write-Host "📊 Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Green
    
    if ($response.StatusCode -eq 200) {
        $tokenData = $response.Content | ConvertFrom-Json
        if ($tokenData.access_token) {
            Write-Host "✅ LOGIN FUNCIONOU! O erro 500 foi resolvido!" -ForegroundColor Green
            Write-Host "🔑 Token: $($tokenData.access_token.Substring(0, 30))..." -ForegroundColor Green
        } else {
            Write-Host "❌ Token não encontrado na resposta" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Falha no login: Status $($response.StatusCode)" -ForegroundColor Red
    }
}
catch {
    if ($_.Exception.Response.StatusCode -eq 500) {
        Write-Host "❌ ERRO 500 AINDA EXISTE - Problema interno do servidor" -ForegroundColor Red
        Write-Host "❌ Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    } else {
        Write-Host "❌ Erro na requisição: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "✅ Teste concluído." -ForegroundColor Yellow