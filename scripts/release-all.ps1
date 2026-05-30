<#
.SYNOPSIS
    Full safe release pipeline:
    1. ensure clean working tree
    2. ensure on main branch
    3. bump patch version
    4. push bump commit
    5. create TestPyPI release tag
    6. verify installation from TestPyPI
    7. create production PyPI release tag
    8. create GitHub Release
#>

function Test-Clean-Tree {
    $status = git status --porcelain
    if ($status) {
        Write-Error "Working tree is not clean. Commit or stash changes first."
        exit 1
    }
}

function Test-Main-Branch {
    $branch = git rev-parse --abbrev-ref HEAD
    if ($branch -ne "main") {
        Write-Error "You must be on 'main' to run release-all.ps1"
        exit 1
    }
}

function Get-Version {
    @"
import tomllib
print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
"@ | python
}

function Test-Tool($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Error "Required tool '$name' is not installed or not in PATH."
        exit 1
    }
}

# -----------------------------
# 0. Tool checks
# -----------------------------
Test-Tool "git"
Test-Tool "python"
Test-Tool "pip"
Test-Tool "bump2version"
Test-Tool "gh"

# -----------------------------
# 1. Ensure clean working tree
# -----------------------------
Test-Clean-Tree

# -----------------------------
# 2. Ensure on main branch
# -----------------------------
Test-Main-Branch

# -----------------------------
# 3. Bump version
# -----------------------------
Write-Host "Bumping patch version..."
bump2version patch

# -----------------------------
# 4. Push bump commit
# -----------------------------
Write-Host "Pushing version bump commit..."
git push
git push --tags

# Reload version after bump
$version = (Get-Version).Trim()
$testTag = "v$version-test"
$prodTag = "v$version"

# -----------------------------
# 5. Create TestPyPI tag
# -----------------------------
Write-Host "Creating TestPyPI tag $testTag"

git rev-parse $testTag 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Error "Tag $testTag already exists"
    exit 1
}

git tag $testTag
git push origin $testTag

Write-Host "TestPyPI tag pushed: $testTag"

# -----------------------------
# 6. Verify installation
# -----------------------------
Write-Host "Waiting 10 seconds for TestPyPI publish..."
Start-Sleep -Seconds 10

Write-Host "Installing from TestPyPI..."
pip install --index-url https://test.pypi.org/simple/ --no-deps textfsm-ai
if ($LASTEXITCODE -ne 0) {
    Write-Error "TestPyPI installation failed. Aborting release."
    exit 1
}

Write-Host "TestPyPI install verified."

# -----------------------------
# 7. Create production tag
# -----------------------------
Write-Host "Creating production tag $prodTag"

git rev-parse $prodTag 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Error "Tag $prodTag already exists"
    exit 1
}

git tag $prodTag
git push origin $prodTag

# -----------------------------
# 8. Create GitHub Release
# -----------------------------
Write-Host "Creating GitHub Release for $prodTag"
gh release create $prodTag --generate-notes

Write-Host "Production release complete."
