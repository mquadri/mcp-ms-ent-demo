import os
import sys
import importlib.util
import json
import re
import glob
import shutil
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MCP_CONFIG_PATH = ".github/mcp.json"
HTTP_TIMEOUT_SECONDS = 10
MCP_ROUTE_EXISTS_STATUSES = {200, 202, 204, 400, 401, 403, 405, 406}
CONTAINER_APP_DOMAIN = ".azurecontainerapps.io"

def check_python_version():
    print("🔍 Checking Python version...")
    if sys.version_info >= (3, 10):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor} detected.")
        return True
    else:
        print(f"   ❌ Python 3.10+ required. Current: {sys.version_info.major}.{sys.version_info.minor}")
        return False

def check_dependencies():
    print("🔍 Checking dependencies...")
    dependencies = [
        "azure.identity",
        "azure.monitor.query",
        "azure.devops",
        "msgraph",
        "azure.cosmos",
        "semantic_kernel",
        "dotenv"
    ]
    missing = []
    for dep in dependencies:
        if importlib.util.find_spec(dep.split('.')[0]) is None:
            missing.append(dep)

    if not missing:
        print("   ✅ All core dependencies installed.")
        return True
    else:
        print(f"   ❌ Missing dependencies: {', '.join(missing)}")
        print("      Run: pip install -r demos/requirements.txt")
        return False

def check_env_file():
    print("🔍 Checking .env file...")
    if os.path.exists(".env"):
        print("   ✅ .env file found.")
        return True
    else:
        if os.path.exists(".env.example"):
            print("   ⚠️  .env file missing. Using defaults (Mock Mode).")
            print("      To use real Azure data, copy .env.example to .env and fill it in.")
            return True
        else:
            print("   ❌ .env and .env.example missing.")
            return False

def check_mock_data():
    print("🔍 Checking mock data...")
    mock_files = [
        "mock_data_scenario_1.json",
        "agents/.data/scenario_3_mock_data.json",
        "mock_data_scenario_5.json"
    ]
    missing = [f for f in mock_files if not os.path.exists(f)]
    if not missing:
        print("   ✅ Mock data files found.")
        return True

    if os.path.exists("demos/mock_data_generator.py"):
        print(f"   ⚠️  Missing generated mock data: {', '.join(missing)}")
        print("      Run when needed: python demos/mock_data_generator.py && python demos/setup_scenario_3.py")
        return True

    print(f"   ❌ Missing mock data: {', '.join(missing)}")
    print("      Run: python demos/mock_data_generator.py && python demos/setup_scenario_3.py")
    return False


def find_placeholders_in_file(path, patterns):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
    except Exception:
        return []
    matches = []
    for p in patterns:
        if re.search(p, data, re.IGNORECASE):
            matches.append(p)
    return matches


def check_mcp_configs():
    """Scan common config files for placeholder values that indicate stale config."""
    print("🔍 Checking MCP configuration files for stale placeholders...")
    patterns = [r"YOUR_", r"your-", r"<your-", r"YOUR_SUBSCRIPTION_ID", r"YOUR_TENANT_ID", r"YOUR_CLIENT_SECRET", r"your-personal-access-token"]
    active_files = [
        ".github/mcp.json",
        ".env",
    ]
    template_files = [
        ".env.example",
        "configuration/copilot-enterprise-settings.json",
        "configuration/vscode-mcp-settings.json",
    ]
    template_files += glob.glob('configuration/*.json')

    problems = {}
    for p in active_files:
        if os.path.exists(p):
            found = find_placeholders_in_file(p, patterns)
            if found:
                problems[p] = found

    template_warnings = {}
    for p in sorted(set(template_files)):
        if os.path.exists(p):
            found = find_placeholders_in_file(p, patterns)
            if found:
                template_warnings[p] = found

    if not problems:
        print("   ✅ No obvious placeholders found in MCP config files.")
        if template_warnings:
            print("   ℹ️  Template/reference files still contain expected placeholders:")
            for f, pats in template_warnings.items():
                print(f"      - {f}: {', '.join(pats)}")
        return True

    print("   ❌ Found placeholder patterns in active config files:")
    for f, pats in problems.items():
        print(f"      - {f}: {', '.join(pats)}")
    print("      Replace placeholders in active config before running in real mode.")
    return False


def check_mcp_routing():
    """Verify routing entries in .github/mcp.json and warn about internal endpoints."""
    print("🔍 Checking MCP routing entries (.github/mcp.json)...")
    path = MCP_CONFIG_PATH
    if not os.path.exists(path):
        print("   ⚠️  .github/mcp.json not found — skipping MCP routing checks.")
        return True
    try:
        with open(path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"   ❌ Failed to parse {path}: {e}")
        return False

    servers = cfg.get('servers') or {}
    issues = []
    for name, info in servers.items():
        t = info.get('type')
        url = info.get('url') or info.get('command') or info.get('args')
        if t == 'http':
            if not url or isinstance(url, str) and re.search(r'your-|YOUR_', str(url), re.IGNORECASE):
                issues.append(f"{name}: invalid url")
            else:
                if isinstance(url, str) and 'internal.' in url:
                    print(f"   ⚠️  {name} uses an internal Container Apps endpoint ({url}). This endpoint is not reachable from your laptop without tunnel/private access.")
                if isinstance(url, str) and is_container_app_mcp_server(name, url):
                    parsed = urlparse(url)
                    if parsed.path.rstrip("/") != "/mcp":
                        issues.append(f"{name}: Container Apps MCP URL must end with /mcp, not {parsed.path or '/'}")
        elif t == 'stdio':
            # basic check that command/args exist
            if not info.get('command') and not info.get('args'):
                issues.append(f"{name}: missing command/args for stdio server")
        else:
            # unknown types are ok but warn
            print(f"   ⚠️  {name} has type '{t}' — please confirm this is intentional.")

    if issues:
        print("   ❌ MCP routing issues found:")
        for it in issues:
            print(f"      - {it}")
        return False
    print("   ✅ MCP routing entries appear valid (basic checks).")
    return True


def is_container_app_mcp_server(name, url):
    parsed = urlparse(url)
    return CONTAINER_APP_DOMAIN in parsed.netloc and "mcp" in name.lower()


def get_http_status(url, method="GET", headers=None):
    req = Request(url, method=method, headers=headers or {})
    try:
        with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return response.status, None
    except HTTPError as exc:
        return exc.code, None
    except URLError as exc:
        return None, exc.reason
    except TimeoutError as exc:
        return None, exc


def check_mcp_sse_endpoints():
    """Probe configured HTTP MCP endpoints for the route used by SSE-capable MCP clients."""
    print("🔍 Checking live MCP HTTP/SSE routes...")
    if not os.path.exists(MCP_CONFIG_PATH):
        print("   ⚠️  .github/mcp.json not found — skipping live MCP route checks.")
        return True

    try:
        with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"   ❌ Failed to parse {MCP_CONFIG_PATH}: {e}")
        return False

    servers = cfg.get("servers") or {}
    http_servers = {
        name: info.get("url")
        for name, info in servers.items()
        if info.get("type") == "http" and info.get("url")
    }
    if not http_servers:
        print("   ⚠️  No HTTP MCP servers configured — skipping live MCP route checks.")
        return True

    ok = True
    for name, url in http_servers.items():
        parsed = urlparse(url)
        if "internal." in parsed.netloc:
            print(f"   ⚠️  {name}: skipping internal endpoint from local probe ({url}).")
            continue

        if is_container_app_mcp_server(name, url) and parsed.path.rstrip("/") != "/mcp":
            print(f"   ❌ {name}: SSE/MCP clients must connect to /mcp; configured path is {parsed.path or '/'}.")
            ok = False
            continue

        headers = {
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2024-11-05",
        }
        status, error = get_http_status(url, headers=headers)
        if status in MCP_ROUTE_EXISTS_STATUSES:
            note = "route exists"
            if status == 406:
                note = "route exists; plain probe is not a full MCP handshake"
            print(f"   ✅ {name}: {url} returned HTTP {status} ({note}).")
        elif status is not None:
            print(f"   ❌ {name}: {url} returned HTTP {status}; expected an MCP route response, not 404/5xx.")
            ok = False
        else:
            print(f"   ❌ {name}: could not reach {url}: {error}")
            ok = False

        if is_container_app_mcp_server(name, url):
            base_url = f"{parsed.scheme}://{parsed.netloc}/"
            base_status, base_error = get_http_status(base_url, headers=headers)
            if base_status == 404:
                print(f"      ℹ️  Base path {base_url} returned 404 as expected; use /mcp for MCP/SSE.")
            elif base_status is not None:
                print(f"      ℹ️  Base path {base_url} returned HTTP {base_status}; configured MCP path remains {parsed.path}.")
            else:
                print(f"      ⚠️  Could not probe base path {base_url}: {base_error}")

    if ok:
        print("   ✅ Live MCP HTTP/SSE route checks passed.")
    return ok


def ensure_warm(revision_name=None):
    """Optional: attempt to warm the container by invoking az if available."""
    if shutil.which('az') is None:
        print("   ℹ️  Azure CLI not available locally — skipping active-warm check.")
        return None
    cmd = ["az", "containerapp", "logs", "show", "--name", "azure-mcp", "--resource-group", "rg-mcp-agent-stack", "--tail", "1"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=" * 50)
    print("🚀 MCP Demo Health Check")
    print("=" * 50)

    results = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_mock_data()
    ]

    # MCP-specific checks
    results.append(check_mcp_configs())
    results.append(check_mcp_routing())
    results.append(check_mcp_sse_endpoints())

    # Attempt to warm container (optional)
    warm = ensure_warm()
    if warm is False:
        print("   ⚠️  Could not fetch logs via Azure CLI — the app may be scaled to zero or CLI not authenticated.")
    elif warm is True:
        print("   ✅ Azure Container Apps responded to a log probe.")

    print("=" * 50)
    if all(results):
        print("✅ Environment is READY for the demo!")
    else:
        print("❌ Environment has ISSUES. Please fix the items above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
