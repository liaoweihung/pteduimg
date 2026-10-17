#Requires -Version 7.0
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$script = Join-Path $PSScriptRoot '../scripts/invoke_review.ps1'
$packet = @{page_ids=@('synthetic_example'); audience='合成讀者'; text="合成文字。`n第二行。"
    previous_text=''; sources=@()}
$json = $packet | ConvertTo-Json -Depth 10 -Compress
$count = 0
function Assert($Condition, [string]$Name) {
    if (!$Condition) { throw "FAILED: $Name" }
    $script:count++
}
function Run([string]$Scenario='Success', [string]$InputJson=$json, [string]$Previous='') {
    $raw = & $script -PacketJson $InputJson -Mode Simulate -Scenario $Scenario -TimeoutSeconds 1 -PreviousResultJson $Previous
    $code = $LASTEXITCODE
    @{data=($raw | ConvertFrom-Json -AsHashtable); raw=$raw; code=$code}
}
$ok = Run
Assert ($ok.code -eq 0 -and $ok.data.state -eq 'COMPLETED' -and $ok.data.simulated -and
    !$ok.data.model_called -and $ok.data.duration_seconds -eq 0.25) 'synthetic success and provenance'
foreach ($case in @(
    @('Failure','CLI_STATUS_NOT_SUCCESS'), @('Incomplete','INCOMPLETE_OUTPUT'),
    @('InvalidJson','INVALID_JSON'), @('BadDuration','INVALID_DURATION'),
    @('BadReview','INVALID_REVIEW'), @('OutOfScope','INVALID_REVIEW'),
    @('BadQuote','INVALID_REVIEW'), @('BadSource','INVALID_REVIEW'), @('NonzeroExit','CLI_EXIT_NONZERO')
)) {
    $r = Run $case[0]
    Assert ($r.code -eq 2 -and $r.data.state -eq 'FAILED' -and $r.data.reason -ceq $case[1]) $case[0]
}
$watch = [Diagnostics.Stopwatch]::StartNew()
$timeout = Run 'Timeout'
Assert ($timeout.code -eq 3 -and $timeout.data.state -eq 'TIMEOUT' -and $watch.Elapsed.TotalSeconds -lt 8) 'host deadline and child cleanup'
$reuse = Run -Previous $ok.raw
Assert ($reuse.data.state -eq 'REUSED') 'same version reused'
$changed = $packet.Clone(); $changed.text += '修訂'
Assert ((Run -InputJson ($changed | ConvertTo-Json -Depth 10 -Compress) -Previous $ok.raw).data.state -eq 'COMPLETED') 'changed text not reused'
$crlf = $json.Replace('\n','\r\n')
Assert ((Run -InputJson $crlf -Previous $ok.raw).data.state -eq 'REUSED') 'line ending normalization'
$prior = $ok.raw | ConvertFrom-Json -AsHashtable; $prior.review_key = 'old'
Assert ((Run -Previous ($prior | ConvertTo-Json -Depth 20 -Compress)).data.state -eq 'COMPLETED') 'changed contract key not reused'
$prior = $ok.raw | ConvertFrom-Json -AsHashtable; $prior.simulated = $false
Assert ((Run -Previous ($prior | ConvertTo-Json -Depth 20 -Compress)).data.state -eq 'COMPLETED') 'provenance domains separate'
$failure = Run 'Failure'
Assert ((Run -Previous $failure.raw).data.state -eq 'COMPLETED') 'failed result never cached'
$invalid = $packet.Clone(); $invalid['extra'] = 'unapproved'
Assert ((Run -InputJson ($invalid | ConvertTo-Json -Depth 10 -Compress)).data.reason -eq 'INVALID_INPUT') 'reject extra input'
$invalid = $packet.Clone(); $invalid.text = 'a' * 24001
Assert ((Run -InputJson ($invalid | ConvertTo-Json -Depth 10 -Compress)).data.reason -eq 'INPUT_TOO_LARGE') 'bounded input'
$invalid = $packet.Clone(); $invalid.page_ids = @('../outside')
Assert ((Run -InputJson ($invalid | ConvertTo-Json -Depth 10 -Compress)).data.state -eq 'FAILED') 'reject path as page ID'
$live = & $script -PacketJson $json -Mode Live -PreviousResultJson $ok.raw | ConvertFrom-Json
Assert ($LASTEXITCODE -eq 2 -and $live.state -eq 'BLOCKED' -and $live.reason -eq 'ISOLATION_UNVERIFIED' -and
    !$live.model_called -and !$live.simulated) 'live blocked even with simulated cache'
$validate = & $script -PacketJson $json -Mode Validate | ConvertFrom-Json
Assert ($LASTEXITCODE -eq 0 -and $validate.state -eq 'VALIDATED' -and $validate.prompt.Contains($packet.text.Replace("`n",'\n'))) 'local prompt validation'
$findings = Run 'Findings'
Assert ($findings.data.state -eq 'COMPLETED' -and $findings.data.review.findings.Count -eq 1) 'valid finding parsed'
$withSources = $packet.Clone()
$withSources.sources = @(
    @{title='來源乙'; url='https://example.org/b'; excerpt='合成乙'},
    @{title='來源甲'; url='https://example.org/a'; excerpt='合成甲'}
)
$sourceResult = Run -InputJson ($withSources | ConvertTo-Json -Depth 10 -Compress)
[Array]::Reverse($withSources.sources)
Assert ((Run -InputJson ($withSources | ConvertTo-Json -Depth 10 -Compress) -Previous $sourceResult.raw).data.state -eq 'REUSED') 'source order canonicalization'
$withSources.sources[0].excerpt = '來源摘錄實質修訂'
Assert ((Run -InputJson ($withSources | ConvertTo-Json -Depth 10 -Compress) -Previous $sourceResult.raw).data.state -eq 'COMPLETED') 'source revision invalidates reuse'
$unicode = $packet.Clone(); $unicode.text = "合成 caf$([char]0xE9)"
$nfc = Run -InputJson ($unicode | ConvertTo-Json -Depth 10 -Compress)
$unicode.text = "合成 cafe$([char]0x301)"
Assert ((Run -InputJson ($unicode | ConvertTo-Json -Depth 10 -Compress) -Previous $nfc.raw).data.state -eq 'REUSED') 'NFC canonicalization'
$audience = $packet.Clone(); $audience.audience = '另一合成受眾'
Assert ((Run -InputJson ($audience | ConvertTo-Json -Depth 10 -Compress) -Previous $ok.raw).data.state -eq 'COMPLETED') 'audience invalidates reuse'
$duplicate = $packet.Clone(); $duplicate.page_ids = @('synthetic_example','synthetic_example')
Assert ((Run -InputJson ($duplicate | ConvertTo-Json -Depth 10 -Compress)).data.state -eq 'FAILED') 'duplicate page IDs rejected'
Write-Output "PASS: $count assertions; synthetic data only; no agy process or network."
