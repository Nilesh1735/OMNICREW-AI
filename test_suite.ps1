# OmniCrew AI - Backend Security & API Test Suite
 $baseUrl = "http://127.0.0.1:8000"
 $passCount = 0
 $failCount = 0

function Test-Feature($name, $condition, $detail) {
    if ($condition) {
        Write-Host "[PASS] $name" -ForegroundColor Green
        $script:passCount++
    } else {
        Write-Host "[FAIL] $name -> $detail" -ForegroundColor Red
        $script:failCount++
    }
}

Write-Host "========================================="
Write-Host " Starting OmniCrew AI Security Test Suite"
Write-Host "=========================================`n"

# 1. Test Backend Health
Write-Host "[*] Testing Backend Health..."
try {
    $res = Invoke-WebRequest -Uri "$baseUrl/docs" -Method GET -UseBasicParsing -TimeoutSec 5
    Test-Feature "Backend is running" ($res.StatusCode -eq 200) "Status was $($res.StatusCode)"
} catch {
    Test-Feature "Backend is running" $false "Backend did not respond. Is Docker running?"
}

# 2. Test IDOR Prevention (No Auth)
Write-Host "`n[*] Testing IDOR Prevention (No Auth Header)..."
try {
    $res = Invoke-WebRequest -Uri "$baseUrl/api/leads" -Method GET -UseBasicParsing -ErrorAction Stop
    Test-Feature "Blocks unauthenticated /leads" $false "Should have returned 401 but got $($res.StatusCode)"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Test-Feature "Blocks unauthenticated /leads" ($code -eq 401) "Expected 401, got $code"
}

# 3. Test IDOR Prevention (With Mock Auth)
Write-Host "`n[*] Testing Authenticated Request (With Mock Token)..."
try {
    $headers = @{ "Authorization" = "Bearer mock_token_123" }
    $res = Invoke-WebRequest -Uri "$baseUrl/api/leads" -Method GET -Headers $headers -UseBasicParsing -ErrorAction Stop
    Test-Feature "Allows authenticated /leads" ($res.StatusCode -eq 200) "Status was $($res.StatusCode)"
} catch {
    Test-Feature "Allows authenticated /leads" $false $_.Exception.Message
}

# 4. Test Transport Security (Blocks HTTP)
Write-Host "`n[*] Testing Transport Security (Blocking HTTP URL)..."
try {
    $headers = @{ "Authorization" = "Bearer mock_token_123"; "Content-Type" = "application/json" }
    $body = '{"task_description": "Find a book", "target_url": "http://books.toscrape.com/"}'
    $res = Invoke-WebRequest -Uri "$baseUrl/api/webhook/start-task" -Method POST -Headers $headers -Body $body -UseBasicParsing -ErrorAction Stop
    Test-Feature "Blocks HTTP target URLs" $false "Should have returned 400 but got $($res.StatusCode)"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Test-Feature "Blocks HTTP target URLs" ($code -eq 400) "Expected 400, got $code"
}

# 5. Test SSRF Protection (Blocks Localhost/Internal IPs)
Write-Host "`n[*] Testing SSRF Protection (Blocking 127.0.0.1)..."
try {
    $headers = @{ "Authorization" = "Bearer mock_token_123"; "Content-Type" = "application/json" }
    $body = '{"task_description": "Steal metadata", "target_url": "https://127.0.0.1/.env"}'
    $res = Invoke-WebRequest -Uri "$baseUrl/api/webhook/start-task" -Method POST -Headers $headers -Body $body -UseBasicParsing -ErrorAction Stop
    
    # If the API accepts it, the agent will try to scrape it. We need to check if the tool blocks it.
    # The API itself might return 200 (queued), so we check the logs or expect a 400 from the validator.
    Test-Feature "Blocks SSRF Internal IPs" $false "Should have returned 400 but got $($res.StatusCode)"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Test-Feature "Blocks SSRF Internal IPs" ($code -eq 400) "Expected 400, got $code"
}

# 6. Test Exposed Files Protection (Blocks /.env on external domain)
Write-Host "`n[*] Testing Exposed Files Protection (Blocking /.env)..."
try {
    $headers = @{ "Authorization" = "Bearer mock_token_123"; "Content-Type" = "application/json" }
    $body = '{"task_description": "Steal config", "target_url": "https://books.toscrape.com/.env"}'
    $res = Invoke-WebRequest -Uri "$baseUrl/api/webhook/start-task" -Method POST -Headers $headers -Body $body -UseBasicParsing -ErrorAction Stop
    Test-Feature "Blocks Exposed Files" $false "Should have returned 400 but got $($res.StatusCode)"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Test-Feature "Blocks Exposed Files" ($code -eq 400) "Expected 400, got $code"
}

# 7. Test Task Initiation (Valid HTTPS)
Write-Host "`n[*] Testing Task Initiation (Valid HTTPS URL)..."
try {
    $headers = @{ "Authorization" = "Bearer mock_token_123"; "Content-Type" = "application/json" }
    $body = '{"task_description": "Find the title of the first book listed and its price.", "target_url": "https://books.toscrape.com/"}'
    $res = Invoke-WebRequest -Uri "$baseUrl/api/webhook/start-task" -Method POST -Headers $headers -Body $body -UseBasicParsing -ErrorAction Stop
    $json = $res.Content | ConvertFrom-Json
    Test-Feature "Successfully initiates valid task" ($res.StatusCode -eq 200 -and $json.status -eq "queued") "Status was $($res.StatusCode)"
} catch {
    Test-Feature "Successfully initiates valid task" $false $_.Exception.Message
}

Write-Host "`n========================================="
Write-Host " Test Summary"
Write-Host "========================================="
Write-Host " Passed: $passCount" -ForegroundColor Green
Write-Host " Failed: $failCount" -ForegroundColor Red
Write-Host "=========================================`n"