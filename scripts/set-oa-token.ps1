[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$secureToken = Read-Host '输入你自己的 RWKV OA MCP Token（输入隐藏）' -AsSecureString
$tokenPointer = [IntPtr]::Zero
try {
    $tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer).Trim()
    if ([string]::IsNullOrWhiteSpace($plainToken)) {
        throw 'Token 不能为空。'
    }
    [Environment]::SetEnvironmentVariable('RWKV_OA_TOKEN', $plainToken, 'User')
    [Environment]::SetEnvironmentVariable('RWKV_OA_TOKEN', $plainToken, 'Process')
    Write-Host '已保存当前用户的 RWKV_OA_TOKEN。请完全退出 Codex 并重新启动。'
} finally {
    if ($tokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
    }
    $plainToken = $null
    $secureToken.Dispose()
}
