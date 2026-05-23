import os
import sys
import importlib.util

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
    else:
        print(f"   ⚠️  Missing mock data: {', '.join(missing)}")
        print("      Run: python demos/setup_scenario_1.py && python demos/setup_scenario_3.py && python demos/setup_scenario_5.py")
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

    print("=" * 50)
    if all(results):
        print("✅ Environment is READY for the demo!")
    else:
        print("❌ Environment has ISSUES. Please fix the items above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
