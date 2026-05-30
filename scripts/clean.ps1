<#
.SYNOPSIS
    Remove Python caches, build artifacts, coverage files, and Ruff caches.
#>

Write-Host "Cleaning Python caches and build artifacts..."

# Bytecode + pycache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# pytest cache
Get-ChildItem -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Ruff cache
Get-ChildItem -Recurse -Directory -Filter ".ruff_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter ".ruffcache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# tox environments
Get-ChildItem -Recurse -Directory -Filter ".tox" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# mymy cache
Get-ChildItem -Recurse -Directory -Filter ".mypy_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Coverage output
Get-ChildItem -Recurse -Directory -Filter "htmlcov" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter ".coverage" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "coverage.xml" | Remove-Item -Force -ErrorAction SilentlyContinue

# Packaging metadata
Get-ChildItem -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Build artifacts
Get-ChildItem -Recurse -Directory -Filter "build" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter "dist" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.whl" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter "*.tar.gz" | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete."
