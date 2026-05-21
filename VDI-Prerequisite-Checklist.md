# VDI Prerequisite Validation Checklist

Use this checklist with `Validate-VDIPrereqs.ps1` to validate a virtual desktop before sign-off. Update the script configuration with the exact State of Wisconsin prerequisites from the source document before running it.

## 1. Validation setup

| Item | Evidence to capture | Status |
| --- | --- | --- |
| Confirm VDI hostname and assigned user | Hostname, username, date/time of validation | Not started |
| Confirm validation is run from the actual VDI image/session | Screenshot or script report path | Not started |
| Confirm source prerequisite document/version | Document name, version/date, owner | Not started |
| Confirm exceptions process | Approved exception ticket or N/A | Not started |

## 2. System prerequisites

| Item | Evidence to capture | Status |
| --- | --- | --- |
| Supported Windows edition and build | Script OS build check | Not started |
| Minimum CPU/vCPU count | Script CPU check | Not started |
| Minimum memory | Script memory check | Not started |
| Minimum free disk space | Script disk check | Not started |
| Required time zone/clock synchronization | Script time check, `w32tm` status | Not started |
| Recent patch/hotfix state | Script hotfix summary | Not started |

## 3. Identity and access

| Item | Evidence to capture | Status |
| --- | --- | --- |
| Domain, workgroup, or Entra ID join state matches requirements | Script domain and `dsregcmd` checks | Not started |
| Test user can sign in successfully | Screenshot or validation notes | Not started |
| Required groups or roles assigned | Group/role evidence from IAM owner | Not started |
| MFA/conditional access behavior works as expected | Sign-in result, policy notes | Not started |

## 4. Network and connectivity

| Item | Evidence to capture | Status |
| --- | --- | --- |
| DNS resolves required hostnames | Script DNS checks | Not started |
| Required TCP ports are reachable | Script TCP connectivity checks | Not started |
| Required URLs are reachable | Script URL checks | Not started |
| Proxy configuration matches requirements | Script proxy check | Not started |
| Firewall rules allow required traffic | Script result plus firewall policy evidence | Not started |
| No unexpected network restrictions in VDI subnet | Network test results or firewall team confirmation | Not started |

## 5. Security and compliance

| Item | Evidence to capture | Status |
| --- | --- | --- |
| Endpoint protection is installed and healthy | Script Defender/AV status or security tooling evidence | Not started |
| Disk encryption state meets requirements | Script BitLocker status | Not started |
| Secure Boot requirement is met, if required | Script Secure Boot check | Not started |
| TPM requirement is met, if required | Script TPM check | Not started |
| Local admin access is restricted as required | Group membership evidence | Not started |
| Screen lock/session timeout policy applies | Policy evidence or manual validation | Not started |

## 6. Required software and configuration

| Item | Evidence to capture | Status |
| --- | --- | --- |
| Required applications are installed | Populate `$RequiredSoftware`; attach script report | Not started |
| Required browser/version is installed | Software evidence and launch test | Not started |
| Required agents are installed and running | Script service/software checks | Not started |
| Required registry settings are present | Populate `$RequiredRegistryValues`; attach script report | Not started |
| Required environment variables are present | Populate `$RequiredEnvironmentVariables`; attach script report | Not started |
| Required certificates are present and trusted | Certificate store evidence | Not started |

## 7. Functional validation

| Item | Evidence to capture | Status |
| --- | --- | --- |
| User can open required websites/apps | Screenshot or test notes | Not started |
| User can access required file shares or storage | Access result or screenshot | Not started |
| Printing/scanning/peripheral access works, if required | Test result or N/A | Not started |
| Clipboard, drive redirection, audio/video, and Teams optimization comply with policy | Test result or policy evidence | Not started |
| Session reconnect/logoff behavior works as expected | Test notes | Not started |

## 8. Sign-off package

| Item | Evidence to capture | Status |
| --- | --- | --- |
| HTML validation report attached | `VDI-Prereq-Report-*.html` | Not started |
| CSV/JSON raw validation results attached | `VDI-Prereq-Results-*.csv` and `.json` | Not started |
| Manual checklist completed | This checklist | Not started |
| Exceptions documented and approved | Exception ticket IDs or N/A | Not started |
| Final validation owner/date captured | Name and date | Not started |

## Running the script

Open PowerShell on the VDI and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\Validate-VDIPrereqs.ps1
```

To skip internet URL checks in a restricted environment:

```powershell
.\Validate-VDIPrereqs.ps1 -SkipInternetChecks
```

The report files are created under:

```text
.\Results
```

## Customization points

Before using this for formal validation, update these script variables:

| Script variable | What to enter |
| --- | --- |
| `$Minimums` | Required memory, disk, CPU, OS build, TPM, Secure Boot |
| `$RequiredServices` | Required Windows services and expected status/start type |
| `$RequiredSoftware` | Required application display names, using wildcards if useful |
| `$RequiredEnvironmentVariables` | Required machine-level environment variables |
| `$RequiredRegistryValues` | Required registry paths, value names, and expected values |
| `$NetworkTargets` | Required host/port combinations |
| `$RequiredUrls` | Required HTTPS/HTTP URLs |
| `$RequiredDnsNames` | Required DNS names |
