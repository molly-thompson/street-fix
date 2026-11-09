# Engineering Conventions & Git Workflow

This document defines the git, branching, and pull request standards for this repository. These conventions are established with the aim of ensuring a clean, traceable history; enabling the automation of changelog generation; and streamlining the code review process.

## 1. Commit Conventions

Commit messages should follow the [Conventional Commits Specification](https://www.conventionalcommits.org/).

### Format

```text
<type>[optional scope]: <short summary in lowercase>

[optional body]

[optional footer(s)]

```

### Types

| Type | Description | Example |
| --- | --- | --- |
| `feat` | A new feature for the user or system | `feat(auth): add google oauth login support` |
| `fix` | A bug fix | `fix(dashboard): resolve grid item overlapping on resize` |
| `docs` | Documentation changes only | `docs(readme): add environment variable setup steps` |
| `style` | Formatting, missing semi-colons, no code logic changes | `style: run biome formatting across src` |
| `refactor` | Code change that neither fixes a bug nor adds a feature | `refactor(api): extract telemetry helper to utility module` |
| `perf` | Code change that improves performance | `perf(db): optimize user retrieval query` |
| `test` | Adding missing tests or correcting existing tests | `test(auth): add unit tests for token validation` |
| `build` | Changes affecting build system or external dependencies | `build: upgrade tanstack start to latest version` |
| `ci` | Changes to CI configuration scripts and workflows | `ci: add github actions workflow for linting` |
| `chore` | Other changes that don't modify src or test files | `chore: update .gitignore patterns` |

### Scopes & Scope Usage

Scopes provide meaningful grouping for related commits across a project's lifecycle and should be chosen deliberately:

* **Align with Architecture:** Scopes should reflect structural components, modules, or domain boundaries of the application (e.g., `auth`, `api`, `dashboard`, `ui`).
* **Reuse Existing Scopes:** Check the project documentation or recent commit history (`git log`) to identify established scopes before introducing a new one. Reuse existing scopes whenever applicable to keep git history filterable and clean.
* **Avoid Arbitrary Scopes:** Never create ad-hoc scopes on a per-commit basis.

Scopes are optional: 

* Omit scope if a commit applies to the repository as a whole (e.g., repository governance or global configuration).
* Omit scope if it adds no meaningful context beyond what is already stated in the type.

### Commit Best Practices

* **Outcome-Focused:** The git diff explains *what* code changed; the commit message must explain *why*. Focus the summary on the functional outcome or architectural intent rather than listing modified files (e.g., `feat(auth): enable persistent sessions across browser restarts` instead of `feat(auth): update session cookie options`).
* **Imperative Mood:** Write the summary line as a command (e.g., `enable` instead of `enabled` or `enables`).
* **Stylistic Consistency:** Start summaries in lowercase, omit trailing periods, and preserve the official branding capitalization for product or package names (e.g., `chore(build): scaffold TanStack Start application` or `fix(db): optimize PostgreSQL query index`).
* **Breaking Changes:** If a commit introduces a backward-incompatible change, signal it with an exclamation mark (`!`) directly after the type/scope (e.g., `feat(api)!: remove deprecated v1 endpoints`) and explain the required migration steps in the commit body.

For more guidance on crafting clear, maintainable commit histories, Chris Beams' [How To Write A Git Commit Message](https://chris.beams.io/git-commit) is an excellent resource.

## 2. Branch Naming Conventions

Branch names should be short, descriptive, and follow the standard prefix structure:

```text
<prefix>/<short-kebab-case-description>

```

### Guidelines

* **Intent-Driven Prefixes:** Choose a prefix that reflects the primary goal of the branch (e.g., `feat/user-auth`, `fix/table-overflow`, `docs/readme-setup`, `refactor/api-client`, `chore/ci-workflow`).
* **Branch vs. Commit Types:** Branch prefixes categorize the overall work stream, but **they do not restrict individual commits**. Commits within a branch must still be typed and scoped independently according to the specific changes made in that exact commit. For example, a branch prefixed with `feat/` can—and should—contain `fix:` or `docs:` commits if those adjustments are made along the way.


## 3. Pull Request Conventions

### Preparing a PR

* **Scope:** PRs should be focused and single-purpose. Small, digestible PRs are reviewed and merged much faster.
* **Self-Review:** Before requesting reviews, ensure your diff meets the repository guidelines: ensure no debug logging, dead code, or temporary commented lines remain.
* **Automated Checks:** Ensure all pre-commit hooks, linter checks, type checks, and tests pass locally prior to pushing.

### PR Title & Description

* **Conventional Commit titles** should be used for PRs (e.g., `feat(auth): implement session persistence`).
* The PR template should be completed, and should be used to provide clear context on **what** was changed and **why**.
* Relevant issues should be linked (e.g., `Closes #12` or `Fixes #45`) to enable automated issue tracking.

## 4. Git History & Merge Strategy

This repository permits only two merge strategies, chosen based on the nature and structure of the work on the branch:

- **Standard Merge:** Preferred for larger feature or refactoring branches where individual commits have been thoughtfully crafted as logical, atomic steps. Preserving this history provides valuable context for how a feature was built and makes code review and debugging easier.
- **Squash and Merge:** Used for smaller updates, quick bug fixes, documentation changes, or branches where intermediate commits (e.g., "fix typo") would add noise rather than value to the `main` history.

Regardless of the merge strategy chosen, the resulting history on `main` should remain readable, purposeful, and aligned with Conventional Commit standards.
