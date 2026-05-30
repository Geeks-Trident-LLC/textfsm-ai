<#
.SYNOPSIS
    Verify that pyproject.toml and textfsm_ai/__init__.py versions match
#>

$pyVersion = python - << 'EOF'
import tomllib
print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
EOF

$initVersion = python - << 'EOF'
import textfsm_ai
print(textfsm_ai.__version__)
EOF

Write-Host "pyproject.toml version: $pyVersion"
Write-Host "__init__.py version:   $initVersion"

if ($pyVersion -ne $initVersion) {
    Write-Error "Version mismatch detected!"
    exit 1
}

Write-Host "Versions match."
