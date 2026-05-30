<#
.SYNOPSIS
    Verify that pyproject.toml and textfsm_ai/__init__.py versions match
#>

# Read version from pyproject.toml
$pyVersion = @"
import tomllib
print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
"@ | python
$pyVersion = $pyVersion.Trim()

# Read version from local textfsm_ai/__init__.py (no install required)
$initVersion = @"
import sys, importlib.util, pathlib

pkg = pathlib.Path("textfsm_ai/__init__.py").resolve()
spec = importlib.util.spec_from_file_location("textfsm_ai", pkg)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(mod.__version__)
"@ | python
$initVersion = $initVersion.Trim()

Write-Host "pyproject.toml version: $pyVersion"
Write-Host "__init__.py version:   $initVersion"

if ($pyVersion -ne $initVersion) {
    Write-Error "Version mismatch detected!"
    exit 1
}

Write-Host "Versions match."
