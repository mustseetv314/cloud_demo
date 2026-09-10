param(
    [Parameter(Mandatory = $true)]
    [string]$BaseUrl
)

$BaseUrl = $BaseUrl.TrimEnd("/")
$Failed = $false

foreach ($Path in @("/", "/health", "/api/info", "/api/customers")) {
    try {
        $Response = Invoke-WebRequest -Uri "$BaseUrl$Path" -Method Get -UseBasicParsing
        if ($Response.StatusCode -eq 200) {
            Write-Host "PASS $Path"
        } else {
            Write-Host "FAIL $Path (HTTP $($Response.StatusCode))"
            $Failed = $true
        }
    } catch {
        Write-Host "FAIL $Path"
        $Failed = $true
    }
}

if ($Failed) { exit 1 }
exit 0
