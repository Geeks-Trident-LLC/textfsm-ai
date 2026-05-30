param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "bump-patch",
        "bump-minor",
        "bump-major",
        "release-test",
        "release-prod"
    )]
    $Command
)

function Get-Version {
    @"
import tomllib
print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])
"@ | python
}

function Update-Version([string]$part) {
    bump2version $part
}

function Publish-Test {
    $version = Get-Version
    $tag = "v$version-test"

    Write-Host "Creating TestPyPI tag $tag"

    git rev-parse $tag 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Error "Tag $tag already exists"
        exit 1
    }

    git tag $tag
    git push origin $tag

    Write-Host "TestPyPI tag pushed: $tag"
}

function Publish-Prod {
    $branch = git rev-parse --abbrev-ref HEAD
    if ($branch -ne "main") {
        Write-Error "Must be on main to release to PyPI"
        exit 1
    }

    $version = Get-Version
    $tag = "v$version"

    git rev-parse $tag 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Error "Tag $tag already exists"
        exit 1
    }

    Write-Host "Creating production tag $tag"

    git tag $tag
    git push origin $tag

    Write-Host "Creating GitHub Release for $tag"
    gh release create $tag --generate-notes
}

switch ($Command) {
    "bump-patch" { Update-Version "patch" }
    "bump-minor" { Update-Version "minor" }
    "bump-major" { Update-Version "major" }
    "release-test" { Publish-Test }
    "release-prod" { Publish-Prod }
}
