# Generate Git Commit and Push to GitHub

Based on the `Instructions` below, follow the `Run` section to create a git commit with a properly formatted conventional commit message and push it to GitHub.

## Instructions

- Generate a concise commit message in the conventional commit format: `<type>: <description>`
- Common types:
  - **feat**: A new feature
  - **fix**: A bug fix
  - **docs**: Documentation only changes
  - **style**: Changes that don't affect code meaning (formatting, whitespace)
  - **refactor**: Code change that neither fixes a bug nor adds a feature
  - **test**: Adding or updating tests
  - **chore**: Maintenance tasks, dependency updates
  - **perf**: Performance improvements
  - **ci**: CI/CD configuration changes
  - **build**: Changes to build system or dependencies
- The `<description>` should be:
  - Present tense (e.g., "add", "fix", "update", not "added", "fixed", "updated")
  - 72 characters or less
  - Descriptive of the actual changes made
  - Lowercase (no capitalization)
  - No period at the end
- Examples:
  - `feat: add user authentication module`
  - `fix: resolve login validation error`
  - `chore: update dependencies to latest versions`
  - `docs: update README with installation steps`
  - `refactor: simplify widget tree structure`
- Analyze the git log output to match the existing commit message style in the repository
- Focus purely on the changes made
- No attribution footer or "Generated with..." messages

## Run

1. Run `git diff HEAD` to understand what changes have been made
2. Run `git log --oneline -10` to see recent commit message style
3. Run `git add -A` to stage all changes
4. Generate a commit message that matches the conventional commit format and repository style
5. Run `git commit -m "<generated_commit_message>"` to create the commit
6. Run `git push` to push the commit to GitHub

## Report

Return the commit message that was used and confirm that the push was successful
