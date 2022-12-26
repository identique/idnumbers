# Release Procedure

## Manual Release

### publish script
The manual release could be made with the [scripts/publish.ps1](scripts/publish.ps1). It supports 3 argumenbts:

1. Version: the version try to release
2. CommitMessage: the commit message we will use to tag the release
3. DryRun: dry run without make any changes

Example:
```powershell
.\scripts\publish.ps1 -Version test -DryRun 1
```

It does the followings:
1. Bump-up version from `setup.py`
2. Setup the virtual env for release
3. Run unit-test
4. Build the release
5. Publish to pypi (may ask username/password)
6. Tag a version

### Push tags

After the execution, it tags a version to the local repo. We need to push to remote:
```shell
git push --tags
```

### Create release

We can go to [release page](https://github.com/microdataxyz/idnumbers/releases/new) to make a new release with the pushed tag. We could use `Generate release notes` button to generate from the predefined release notes.

*Please don't forget to check `Create a discussion for this release` checkbox*
