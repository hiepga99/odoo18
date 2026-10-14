$ErrorActionPreference = "Stop"

$AgentDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $AgentDir ".venv\Scripts\python.exe"
$Chroma = Join-Path $AgentDir ".venv\Scripts\chroma.exe"
$DataDir = Join-Path $AgentDir "chroma_server_data"
$LogDir = Join-Path $AgentDir "logs"

if (-not (Test-Path $Python) -or -not (Test-Path $Chroma)) {
    throw "Chưa có .venv đầy đủ. Hãy chạy pip install -r requirements.txt trước."
}

New-Item -ItemType Directory -Force -Path $DataDir, $LogDir | Out-Null

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync("127.0.0.1", $Port)
        return $task.Wait(500) -and $client.Connected
    }
    catch { return $false }
    finally { $client.Dispose() }
}

if (-not (Test-LocalPort 8000)) {
    Start-Process -FilePath $Chroma `
        -ArgumentList @("run", "--path", $DataDir, "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $AgentDir -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir "chroma.out.log") `
        -RedirectStandardError (Join-Path $LogDir "chroma.err.log")
    for ($attempt = 0; $attempt -lt 30 -and -not (Test-LocalPort 8000); $attempt++) {
        Start-Sleep -Milliseconds 500
    }
}

if (-not (Test-LocalPort 8000)) {
    throw "ChromaDB không khởi động được. Xem agent-service\logs\chroma.err.log."
}

$WorkerExists = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match "rag\.odoo\.worker" -and $_.ProcessId -ne $PID
}
if (-not $WorkerExists) {
    $WorkerProcess = Start-Process -FilePath $Python -ArgumentList @("-m", "rag.odoo.worker") `
        -WorkingDirectory $AgentDir -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir "rag-worker.out.log") `
        -RedirectStandardError (Join-Path $LogDir "rag-worker.err.log") -PassThru
    Start-Sleep -Seconds 1
    if ($WorkerProcess.HasExited) {
        throw "RAG worker không khởi động được. Xem agent-service\logs\rag-worker.err.log."
    }
}

Write-Host "RAG local stack đã chạy."
Write-Host "- ChromaDB HTTP: http://127.0.0.1:8000"
Write-Host "- Worker log: $LogDir\rag-worker.out.log"
Write-Host "- Trong Odoo: AI Agent > Kho tài liệu / Nội dung đã làm sạch"
