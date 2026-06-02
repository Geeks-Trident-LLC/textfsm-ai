param(
    [string]$tag
)

# 1. Check if tag exists locally
$localTagExists = git tag --list $tag

if ($localTagExists) {
    Write-Host "Tag $tag already exists locally. Skipping tag creation."
}
else {
    Write-Host "Creating local tag $tag"
    git tag $tag
}

# 2. Check if tag exists on origin
$remoteTagExists = git ls-remote --tags origin $tag

if ($remoteTagExists) {
    Write-Host "Tag $tag already exists on origin. Skipping push."
}
else {
    Write-Host "Pushing tag $tag to origin"
    git push origin $tag
}

# 3. Create or update GitHub Release
if (gh release view $tag 2>$null) {
    Write-Host "GitHub Release for $tag already exists. Updating notes."
    gh release edit $tag --generate-notes
}
else {
    Write-Host "Creating GitHub Release for $tag"
    gh release create $tag --generate-notes
}

Write-Host "release-prod completed successfully."
