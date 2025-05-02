# Source Control and Versioning

## Version Numbering

KCWorks uses semantic versioning (https://semver.org/). When a new release is made, the version number should be incremented in the following files:

- `README.md`
- `docs/source/README.md`
- `docs/source/conf.py`
- `site/pyproject.toml`
- `site/kcworks/__init__.py`

While in beta, the version number should be followed by a numbered `-beta` suffix: e.g., `0.3.3-beta6`. This suffix should be updated continuously (without starting over again for minor releases) until version 1.0.0 is reached and KCWorks leaves beta.

Bug fixes and other changes that do not introduce new features (including changes to documentation, build processes, etc.) should be considered `patch` releases.

New features should be considered `minor` releases.

## Version Control

### Git Branching Strategy

KCWorks employs a modified version of the Gitlab Flow branching strategy for version control. The repository has four persistent branches:

- `main` is the default branch and is the reference point for active development. It will usually not be ready for production deployment.
- `staging` is the branch that is deployed to the staging server. It is created from the `main` branch when changes are ready to be tested. No commits should be made directly to the `staging` branch except to merge changes from `main`.
- `production` is the branch that is deployed to the development server. It is created from the `staging` branch when changes are ready to be deployed to the production server. No commits should be made directly to the `production` branch except to merge changes from `staging`.
- `gh_pages` is the branch that is used to generate the static documentation site for KCWorks on Github Pages. This branch is automatically updated from the `main` branch.

#### Daily Development Workflow

When a developer needs to make changes to the codebase, they should create a new temporary working branch from the `main` branch. This branch should be named descriptively, such as `feature/new-feature` or `fix/fix-issue`. Work in progress should be committed to this working branch until the developer is ready to merge the changes into the `main` branch.

Changes should be merged back into `main` as often as possible, and the temporary branches deleted. These merges should be performed when a developer is ready to deploy the changes to the staging server for testing. This should generally be done *after* the appropriate tests have been written and are passing. Merges should also represent a single completed change (feature or fix). Developers should, though, think in terms of small, incremental changes and merge often.

Merging to `main` should be done via pull request, and the merge only accepted if the newly added tests are present and passing. This ensures that the `main` branch is always in a deployable state and ready for incoming merges by other developers.

```{note}
Merges into `main` should be performed using the `squash` merge strategy (the equivalent of `git merge --squash <branch>`). This combines all of the incoming changes into a single commit, making the commit history cleaner and easier to read.
```

No commits should be made directly to the `staging` or `production` branches. All changes should be made to the `main` branch and then merged into `staging` and `production` via pull requests. This is especially important because changes pushed to `staging` and `production` branches will automatically trigger rebuilding of the stanging or production containers and the deployment of the updated containers to the respective servers.

```{note}
Pull requests to staging and production should be merged using the `rebase` merge strategy, so that the commit history for these branches is kept clean and identical to the `main` branch.
```

### Commit strategy

Developers should make frequent commits to their working branch. These may be as small and granular as the developer wishes since many incremental commits allow easy rollback to specific points in the development history. Such commits should be given descriptive names and commit messages that would allow quick identification of the changes. These commits will be squashed into a single commit when merged into `main`.

Commits to the `main` branch should each represent a single completed change (feature or fix). We try to avoid `wip` commits in order to keep the commit history readable. So all of the changes for a single feature or fix should be squashed into a single commit when merged from a temporary working branch into `main`.

Commits to the `main` branch should be named with the `feature` or `fix` prefix and one or more labels for the aspect of the codebase that the changes address. For example, `feature(upload-form): add a new upload form` or `fix(record-page): fix the problem with the record page`. In general, maintenance changes should be considered `fix` commits unless they are part of a larger feature or add new functionality.

### Tagging Releases

Whenever the KCWorks version number changes, that commit should be tagged with the new version number. This can be done by running the following command:

```shell
git tag -a <version-number> -m "Release <version-number>"
```
We do not create branches for each numbered release.

### Git Submodules

KCWorks uses git submodules to manage dependencies. The submodules are located in the `site/kcworks/dependencies` folder. The submodules are cloned from the upstream repositories when the KCWorks instance is first created. They are updated from the upstream repositories when the KCWorks instance is updated.

Note that in some cases there are inter-dependencies between these submodules. For example, the `invenio-record-importer-kcworks` submodule has its own dependency on the `invenio-group-collections-kcworks` submodule. When cloning the KCWorks repository, you **should not use the `--recurse-submodules` option** because this will clone redundant copies of these inter-dependent submodules. Instead, you should clone the KCWorks repository and then initialize the submodules in a separate step with `git submodule update --init`. Likewise, when updating the KCWorks submodules, you should use the `git submodule update --remote` command **without the `--recursive` option**.

