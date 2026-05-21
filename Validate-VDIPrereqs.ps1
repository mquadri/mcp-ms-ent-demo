<#
.SYNOPSIS
Validates common virtual desktop prerequisites and produces evidence files.

.DESCRIPTION
This script is designed as a configurable starting point for VDI prerequisite
validation. Update the CONFIGURATION section with the exact State of Wisconsin
requirements from the prerequisite document, then run from the virtual desktop.

Outputs:
- HTML summary report
- CSV result table
- JSON result data

.EXAMPLE
.\Validate-VDIPrereqs.ps1

.EXAMPLE
.\Validate-VDIPrereqs.ps1 -OutputDirectory C:\Temp\VDI-Prereq-Results -Verbose
#>

[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot "Results"),
    [switch]$SkipInternetChecks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# -----------------------------
# CONFIGURATION
# -----------------------------
# Replace these sample values with the exact prerequisite values from the
# State of Wisconsin prerequisite document.

$Minimums = @{
    MemoryGB          = 8
    FreeDiskGB        = 20
    CpuCores          = 2
    MinOsBuild        = 19045
    RequireSecureBoot = $false
    RequireTpm        = $false
}

$RequiredServices = @(
    @{ Name = "WinRM";       ExpectedStatus = "Running"; ExpectedStartType = "Automatic" },
    @{ Name = "EventLog";    ExpectedStatus = "Running"; ExpectedStartType = "Automatic" },
    @{ Name = "TermService"; ExpectedStatus = "Running"; ExpectedStartType = "Manual" }
)

$RequiredSoftware = @(
    # DisplayName supports wildcards.
    # Examples:
    # @{ DisplayName = "Microsoft Edge*" },
    # @{ DisplayName = "Microsoft Teams*" },
    # @{ DisplayName = "Microsoft 365 Apps*" }
)

$RequiredEnvironmentVariables = @(
    # Examples:
    # @{ Name = "HTTP_PROXY"; Required = $false },
    # @{ Name = "HTTPS_PROXY"; Required = $false }
)

$RequiredRegistryValues = @(
    # Examples:
    # @{ Path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"; Name = "EnableLUA"; ExpectedValue = 1 }
)

$NetworkTargets = @(
    # Replace/add endpoints required by the prerequisite document.
    @{ Name = "Microsoft login"; Host = "login.microsoftonline.com"; Port = 443 },
    @{ Name = "Microsoft Graph"; Host = "graph.microsoft.com"; Port = 443 },
    @{ Name = "Windows Update"; Host = "windowsupdate.microsoft.com"; Port = 443 }
)

$RequiredUrls = @(
    # Replace/add web URLs that must be reachable from the VDI.
    "https://login.microsoftonline.com/",
    "https://graph.microsoft.com/"
)

$RequiredDnsNames = @(
    "login.microsoftonline.com",
    "graph.microsoft.com"
)

# -----------------------------
# HELPERS
# -----------------------------

$script:Results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param(
        [Parameter(Mandatory)] [string]$Category,
        [Parameter(Mandatory)] [string]$Check,
        [Parameter(Mandatory)] [ValidateSet("Pass", "Fail", "Warning", "Info", "Skipped")] [string]$Status,
        [Parameter(Mandatory)] [string]$Expected,
        [Parameter(Mandatory)] [string]$Actual,
        [string]$Evidence = ""
    )

    $script:Results.Add([pscustomobject]@{
        Timestamp = (Get-Date).ToString("s")
        Computer  = $env:COMPUTERNAME
        User      = "$env:USERDOMAIN\$env:USERNAME"
        Category  = $Category
        Check     = $Check
        Status    = $Status
        Expected  = $Expected
        Actual    = $Actual
        Evidence  = $Evidence
    })
}

function Invoke-Check {
    param(
        [Parameter(Mandatory)] [string]$Category,
        [Parameter(Mandatory)] [string]$Check,
        [Parameter(Mandatory)] [string]$Expected,
        [Parameter(Mandatory)] [scriptblock]$ScriptBlock
    )

    try {
        $result = & $ScriptBlock
        Add-Result -Category $Category -Check $Check -Status $result.Status -Expected $Expected -Actual $result.Actual -Evidence $result.Evidence
    }
    catch {
        Add-Result -Category $Category -Check $Check -Status "Fail" -Expected $Expected -Actual $_.Exception.Message -Evidence "Exception"
    }
}

function ConvertTo-CheckResult {
    param(
        [Parameter(Mandatory)] [bool]$Passed,
        [Parameter(Mandatory)] [string]$Actual,
        [string]$Evidence = "",
        [string]$FailStatus = "Fail"
    )

    [pscustomobject]@{
        Status   = if ($Passed) { "Pass" } else { $FailStatus }
        Actual   = $Actual
        Evidence = $Evidence
    }
}

function Get-InstalledPrograms {
    $registryPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    foreach ($path in $registryPaths) {
        Get-ItemProperty -Path $path -ErrorAction SilentlyContinue |
            Where-Object {
                $null -ne $_.PSObject.Properties["DisplayName"] -and
                -not [string]::IsNullOrWhiteSpace([string]$_.DisplayName)
            } |
            Select-Object DisplayName, DisplayVersion, Publisher, InstallDate
    }
}

function Test-UrlReachability {
    param([Parameter(Mandatory)] [string]$Url)

    $response = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing -TimeoutSec 20
    "HTTP $([int]$response.StatusCode) $($response.StatusDescription)"
}

function Test-TcpPort {
    param(
        [Parameter(Mandatory)] [string]$HostName,
        [Parameter(Mandatory)] [int]$Port,
        [int]$TimeoutMilliseconds = 5000
    )

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $asyncResult = $client.BeginConnect($HostName, $Port, $null, $null)
        $connected = $asyncResult.AsyncWaitHandle.WaitOne($TimeoutMilliseconds, $false)
        if (-not $connected) {
            return [pscustomobject]@{
                Succeeded = $false
                Detail    = "Timed out after $TimeoutMilliseconds ms"
            }
        }

        $client.EndConnect($asyncResult)
        return [pscustomobject]@{
            Succeeded = $true
            Detail    = "Connected to $($client.Client.RemoteEndPoint)"
        }
    }
    catch {
        return [pscustomobject]@{
            Succeeded = $false
            Detail    = $_.Exception.Message
        }
    }
    finally {
        $client.Dispose()
    }
}

function Get-BitLockerSummary {
    try {
        $volumes = Get-BitLockerVolume -ErrorAction Stop
        if (-not $volumes) {
            return "No BitLocker volumes returned"
        }

        return ($volumes | ForEach-Object {
            "$($_.MountPoint): $($_.VolumeStatus), Protection=$($_.ProtectionStatus)"
        }) -join "; "
    }
    catch {
        return "BitLocker check unavailable: $($_.Exception.Message)"
    }
}

function New-HtmlReport {
    param(
        [Parameter(Mandatory)] [object[]]$Rows,
        [Parameter(Mandatory)] [string]$Path
    )

    $summary = $Rows | Group-Object Status | Sort-Object Name | ForEach-Object {
        "<tr><td>$($_.Name)</td><td>$($_.Count)</td></tr>"
    }

    $detailRows = $Rows | ForEach-Object {
        $class = $_.Status.ToLowerInvariant()
        "<tr class='$class'><td>$($_.Status)</td><td>$($_.Category)</td><td>$($_.Check)</td><td>$($_.Expected)</td><td>$($_.Actual)</td><td>$($_.Evidence)</td></tr>"
    }

    $html = @"
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>VDI Prerequisite Validation Report</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f1f1f; }
    h1, h2 { color: #0f6cbd; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; }
    th, td { border: 1px solid #d1d1d1; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f2f1; }
    .pass td:first-child { color: #107c10; font-weight: 600; }
    .fail td:first-child { color: #a4262c; font-weight: 600; }
    .warning td:first-child { color: #8a6d00; font-weight: 600; }
    .skipped td:first-child { color: #605e5c; font-weight: 600; }
    .info td:first-child { color: #0f6cbd; font-weight: 600; }
    .meta { color: #605e5c; }
  </style>
</head>
<body>
  <h1>VDI Prerequisite Validation Report</h1>
  <p class="meta">Computer: $env:COMPUTERNAME<br>User: $env:USERDOMAIN\$env:USERNAME<br>Generated: $(Get-Date)</p>
  <h2>Summary</h2>
  <table>
    <thead><tr><th>Status</th><th>Count</th></tr></thead>
    <tbody>$($summary -join "`n")</tbody>
  </table>
  <h2>Details</h2>
  <table>
    <thead><tr><th>Status</th><th>Category</th><th>Check</th><th>Expected</th><th>Actual</th><th>Evidence</th></tr></thead>
    <tbody>$($detailRows -join "`n")</tbody>
  </table>
</body>
</html>
"@

    Set-Content -Path $Path -Value $html -Encoding UTF8
}

# -----------------------------
# VALIDATION
# -----------------------------

New-Item -Path $OutputDirectory -ItemType Directory -Force | Out-Null

Add-Result -Category "System" -Check "Execution context" -Status "Info" -Expected "Script can run on VDI" -Actual "PowerShell $($PSVersionTable.PSVersion); ProcessArchitecture=$([System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture)" -Evidence "OutputDirectory=$OutputDirectory"

Invoke-Check -Category "System" -Check "Operating system build" -Expected "Windows build >= $($Minimums.MinOsBuild)" -ScriptBlock {
    $os = Get-CimInstance Win32_OperatingSystem
    $build = [int]$os.BuildNumber
    ConvertTo-CheckResult -Passed ($build -ge $Minimums.MinOsBuild) -Actual "$($os.Caption), Version $($os.Version), Build $build" -Evidence "Win32_OperatingSystem"
}

Invoke-Check -Category "System" -Check "CPU cores" -Expected "Logical processors >= $($Minimums.CpuCores)" -ScriptBlock {
    $cpu = Get-CimInstance Win32_Processor
    $logicalProcessors = ($cpu | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
    ConvertTo-CheckResult -Passed ($logicalProcessors -ge $Minimums.CpuCores) -Actual "$logicalProcessors logical processor(s)" -Evidence (($cpu | Select-Object -ExpandProperty Name) -join "; ")
}

Invoke-Check -Category "System" -Check "Memory" -Expected "Total memory >= $($Minimums.MemoryGB) GB" -ScriptBlock {
    $system = Get-CimInstance Win32_ComputerSystem
    $memoryGb = [math]::Round($system.TotalPhysicalMemory / 1GB, 2)
    ConvertTo-CheckResult -Passed ($memoryGb -ge $Minimums.MemoryGB) -Actual "$memoryGb GB" -Evidence "Win32_ComputerSystem.TotalPhysicalMemory"
}

Invoke-Check -Category "System" -Check "System drive free space" -Expected "Free space >= $($Minimums.FreeDiskGB) GB" -ScriptBlock {
    $drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeGb = [math]::Round($drive.FreeSpace / 1GB, 2)
    $sizeGb = [math]::Round($drive.Size / 1GB, 2)
    ConvertTo-CheckResult -Passed ($freeGb -ge $Minimums.FreeDiskGB) -Actual "$freeGb GB free of $sizeGb GB" -Evidence "C:"
}

Invoke-Check -Category "Security" -Check "Secure Boot" -Expected "Secure Boot required: $($Minimums.RequireSecureBoot)" -ScriptBlock {
    if (-not $Minimums.RequireSecureBoot) {
        return [pscustomobject]@{ Status = "Skipped"; Actual = "Not required by current script configuration"; Evidence = "Set RequireSecureBoot to true if required" }
    }

    $secureBoot = Confirm-SecureBootUEFI
    ConvertTo-CheckResult -Passed ([bool]$secureBoot) -Actual "SecureBoot=$secureBoot" -Evidence "Confirm-SecureBootUEFI"
}

Invoke-Check -Category "Security" -Check "TPM" -Expected "TPM required: $($Minimums.RequireTpm)" -ScriptBlock {
    if (-not $Minimums.RequireTpm) {
        return [pscustomobject]@{ Status = "Skipped"; Actual = "Not required by current script configuration"; Evidence = "Set RequireTpm to true if required" }
    }

    $tpm = Get-Tpm
    ConvertTo-CheckResult -Passed ($tpm.TpmPresent -and $tpm.TpmReady) -Actual "Present=$($tpm.TpmPresent); Ready=$($tpm.TpmReady); Enabled=$($tpm.TpmEnabled)" -Evidence "Get-Tpm"
}

Invoke-Check -Category "Security" -Check "BitLocker status" -Expected "Document encryption/protection state" -ScriptBlock {
    [pscustomobject]@{ Status = "Info"; Actual = (Get-BitLockerSummary); Evidence = "Get-BitLockerVolume" }
}

Invoke-Check -Category "Identity" -Check "Domain/workgroup" -Expected "Joined to expected domain or Entra ID per prerequisite document" -ScriptBlock {
    $computerSystem = Get-CimInstance Win32_ComputerSystem
    $joinText = if ($computerSystem.PartOfDomain) { "Domain=$($computerSystem.Domain)" } else { "Workgroup=$($computerSystem.Workgroup)" }
    [pscustomobject]@{ Status = "Info"; Actual = $joinText; Evidence = "Win32_ComputerSystem" }
}

Invoke-Check -Category "Identity" -Check "Entra ID join status" -Expected "Confirm AzureAdJoined/DomainJoined matches prerequisite document" -ScriptBlock {
    $dsreg = & dsregcmd.exe /status 2>$null
    $joinLines = $dsreg | Where-Object { $_ -match "AzureAdJoined|DomainJoined|WorkplaceJoined|TenantName|TenantId" }
    [pscustomobject]@{ Status = "Info"; Actual = (($joinLines -join "; ") -replace "\s+", " ").Trim(); Evidence = "dsregcmd /status" }
}

Invoke-Check -Category "Time" -Check "Windows Time service" -Expected "Time service present and time source documented" -ScriptBlock {
    $status = & w32tm.exe /query /status 2>$null
    [pscustomobject]@{ Status = "Info"; Actual = (($status | Select-Object -First 8) -join "; "); Evidence = "w32tm /query /status" }
}

foreach ($serviceRequirement in $RequiredServices) {
    Invoke-Check -Category "Services" -Check "Service $($serviceRequirement.Name)" -Expected "Status=$($serviceRequirement.ExpectedStatus); StartType=$($serviceRequirement.ExpectedStartType)" -ScriptBlock {
        $service = Get-Service -Name $serviceRequirement.Name -ErrorAction Stop
        $statusMatches = [string]$service.Status -eq $serviceRequirement.ExpectedStatus
        $startTypeMatches = [string]$service.StartType -eq $serviceRequirement.ExpectedStartType
        ConvertTo-CheckResult -Passed ($statusMatches -and $startTypeMatches) -Actual "Status=$($service.Status); StartType=$($service.StartType)" -Evidence $serviceRequirement.Name
    }
}

$installedPrograms = @(Get-InstalledPrograms)
foreach ($software in $RequiredSoftware) {
    Invoke-Check -Category "Software" -Check "Installed software $($software.DisplayName)" -Expected "Installed: $($software.DisplayName)" -ScriptBlock {
        $match = $installedPrograms | Where-Object { $_.DisplayName -like $software.DisplayName } | Select-Object -First 1
        ConvertTo-CheckResult -Passed ($null -ne $match) -Actual $(if ($match) { "$($match.DisplayName) $($match.DisplayVersion)" } else { "Not found" }) -Evidence "Uninstall registry"
    }
}

if ($RequiredSoftware.Count -eq 0) {
    Add-Result -Category "Software" -Check "Required software list" -Status "Warning" -Expected "Populate RequiredSoftware from prerequisite document" -Actual "No required software configured" -Evidence "CONFIGURATION section"
}

foreach ($variable in $RequiredEnvironmentVariables) {
    Invoke-Check -Category "Configuration" -Check "Environment variable $($variable.Name)" -Expected "Required=$($variable.Required)" -ScriptBlock {
        $value = [Environment]::GetEnvironmentVariable($variable.Name, "Machine")
        $exists = -not [string]::IsNullOrWhiteSpace($value)
        $passed = if ($variable.Required) { $exists } else { $true }
        ConvertTo-CheckResult -Passed $passed -Actual $(if ($exists) { "Set" } else { "Not set" }) -Evidence "Machine environment"
    }
}

foreach ($registryValue in $RequiredRegistryValues) {
    Invoke-Check -Category "Configuration" -Check "Registry $($registryValue.Path)\$($registryValue.Name)" -Expected "Value=$($registryValue.ExpectedValue)" -ScriptBlock {
        $item = Get-ItemProperty -Path $registryValue.Path -Name $registryValue.Name -ErrorAction Stop
        $property = $item.PSObject.Properties[$registryValue.Name]
        if ($null -eq $property) {
            throw "Registry value not found: $($registryValue.Path)\$($registryValue.Name)"
        }
        $actualValue = $property.Value
        ConvertTo-CheckResult -Passed ($actualValue -eq $registryValue.ExpectedValue) -Actual "Value=$actualValue" -Evidence $registryValue.Path
    }
}

foreach ($dnsName in $RequiredDnsNames) {
    Invoke-Check -Category "Network" -Check "DNS resolution $dnsName" -Expected "DNS resolves" -ScriptBlock {
        $records = Resolve-DnsName -Name $dnsName -ErrorAction Stop
        $addresses = ($records | Where-Object IPAddress | Select-Object -ExpandProperty IPAddress) -join ", "
        ConvertTo-CheckResult -Passed (-not [string]::IsNullOrWhiteSpace($addresses)) -Actual $addresses -Evidence "Resolve-DnsName"
    }
}

foreach ($target in $NetworkTargets) {
    Invoke-Check -Category "Network" -Check "TCP connectivity $($target.Name)" -Expected "$($target.Host):$($target.Port) reachable" -ScriptBlock {
        $connection = Test-TcpPort -HostName $target.Host -Port $target.Port
        ConvertTo-CheckResult -Passed ([bool]$connection.Succeeded) -Actual $connection.Detail -Evidence "$($target.Host):$($target.Port)"
    }
}

if ($SkipInternetChecks) {
    foreach ($url in $RequiredUrls) {
        Add-Result -Category "Network" -Check "URL reachability $url" -Status "Skipped" -Expected "HTTP reachable" -Actual "Skipped by -SkipInternetChecks" -Evidence $url
    }
}
else {
    foreach ($url in $RequiredUrls) {
        Invoke-Check -Category "Network" -Check "URL reachability $url" -Expected "HTTP response received" -ScriptBlock {
            $actual = Test-UrlReachability -Url $url
            ConvertTo-CheckResult -Passed ($actual -match "HTTP [123]") -Actual $actual -Evidence $url -FailStatus "Warning"
        }
    }
}

Invoke-Check -Category "Network" -Check "Proxy configuration" -Expected "Document proxy state" -ScriptBlock {
    $winHttpProxy = (& netsh.exe winhttp show proxy 2>$null) -join "; "
    [pscustomobject]@{ Status = "Info"; Actual = $winHttpProxy; Evidence = "netsh winhttp show proxy" }
}

Invoke-Check -Category "Network" -Check "IP configuration" -Expected "Document active network adapters" -ScriptBlock {
    $adapters = Get-NetIPConfiguration |
        Where-Object { $_.IPv4Address } |
        ForEach-Object { "$($_.InterfaceAlias): IPv4=$($_.IPv4Address.IPAddress); DNS=$($_.DNSServer.ServerAddresses -join ',')" }
    [pscustomobject]@{ Status = "Info"; Actual = ($adapters -join "; "); Evidence = "Get-NetIPConfiguration" }
}

Invoke-Check -Category "Updates" -Check "Last installed hotfixes" -Expected "Document recent update state" -ScriptBlock {
    $hotfixes = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
    [pscustomobject]@{ Status = "Info"; Actual = (($hotfixes | ForEach-Object { "$($_.HotFixID) $($_.InstalledOn)" }) -join "; "); Evidence = "Get-HotFix" }
}

Invoke-Check -Category "Security" -Check "Defender status" -Expected "Document antimalware state" -ScriptBlock {
    try {
        $defender = Get-MpComputerStatus -ErrorAction Stop
        [pscustomobject]@{ Status = "Info"; Actual = "AMServiceEnabled=$($defender.AMServiceEnabled); RealTimeProtectionEnabled=$($defender.RealTimeProtectionEnabled); AntivirusSignatureLastUpdated=$($defender.AntivirusSignatureLastUpdated)"; Evidence = "Get-MpComputerStatus" }
    }
    catch {
        [pscustomobject]@{ Status = "Warning"; Actual = "Defender status unavailable: $($_.Exception.Message)"; Evidence = "Get-MpComputerStatus" }
    }
}

# -----------------------------
# OUTPUT
# -----------------------------

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = Join-Path $OutputDirectory "VDI-Prereq-Results-$timestamp.csv"
$jsonPath = Join-Path $OutputDirectory "VDI-Prereq-Results-$timestamp.json"
$htmlPath = Join-Path $OutputDirectory "VDI-Prereq-Report-$timestamp.html"

$script:Results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
$script:Results | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8
New-HtmlReport -Rows $script:Results -Path $htmlPath

$summaryText = $script:Results |
    Group-Object Status |
    Sort-Object Name |
    ForEach-Object { "$($_.Name): $($_.Count)" }

Write-Host "VDI prerequisite validation complete." -ForegroundColor Green
Write-Host ($summaryText -join " | ")
Write-Host "HTML: $htmlPath"
Write-Host "CSV : $csvPath"
Write-Host "JSON: $jsonPath"

if (($script:Results | Where-Object Status -eq "Fail").Count -gt 0) {
    exit 1
}
