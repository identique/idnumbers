param ($Version, $CommitMessage, $DryRun)

# setup the env to stop everything on error
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:ErrorAction']='Stop'

if ($null -eq $Version) {
    Write-Output "[ERROR] Version is required."
    exit -1
}

# Phase 1: bump version
Write-Output "[$(Get-Date)] - Dry Run => [$($null -ne $DryRun)]"
Write-Output "[$(Get-Date)] - bump version to $Version"
if ($null -eq $CommitMessage) {
    $message = "Release $Version"
} else {
    $message = $CommitMessage
}

# read the content
if ($null -eq $DryRun) {
    # not dry run, modify and commit
    Write-Output "[$(Get-Date)] - update file VERSION"
    $Version | Set-Content -NoNewline VERSION
    Write-Output "[$(Get-Date)] - commit version update $Version with message '$message'"
    git reset
    git add VERSION
    git commit -m "$message"
} else {
    # output to console
    Write-Output "[$(Get-Date)] - update file VERSION"
    Write-Output "[$(Get-Date)] - DryRun modify: $Version"
}

## Pre-phase 2 - Ensure Environment
if (!(Test-Path -Path "publish_env")) {
    # no publish_env found, let's create one
    Write-Output "[$(Get-Date)] - create publish_env"
    python -m virtualenv publish_env
}
# activate publish env and update 3rd party dependencies
Write-Output "[$(Get-Date)] - activate publish_env"
& "publish_env/Scripts/activate.ps1"
Write-Output "[$(Get-Date)] - ensure 3rd party dependencies"
pip install -r "scripts/publish/requirements.txt"

## Phase 2 - test
Write-Output "[$(Get-Date)] - test"
& "scripts/test.ps1"
## Phase 3 - build
Write-Output "[$(Get-Date)] - build"
python -m build --outdir "dist/$Version"
twine check "dist/$Version/*"
if ($null -eq $DryRun) {
    ## Phase 4 publish to pypi
    Write-Output "[$( Get-Date )] - publish"
    twine upload --verbose "dist/$Version/*"
    # add the tag
    Write-Output "[$( Get-Date )] - add tag $Version"
    git tag -a "v$Version" -m "$message"
} else {
    Write-Output "[$( Get-Date )] - DryRun - publish and add tag"
}
