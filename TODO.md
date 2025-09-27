# TODO

## Git-Cliff / Changelog Improvements

### Idea: Use Merge Commit Body as Documentation

* **Context**: Normally, only the commit subject is included in changelogs.
* **Idea**: Treat merge commits as *project documentation*.

  * The subject line = headline of the feature / branch.
  * The body = narrative explanation of what the branch accomplished.
  * Child commits = detailed steps, already included under the merge.

### Benefits

* Provides more context for each feature branch.
* Turns the changelog into a lightweight project documentation.
* Keeps individual commits small and clean while still showing the bigger picture.
* Optional: if no body is present, nothing changes.

### Possible Implementation

* In the changelog template:

  * Detect merge commits.
  * Render `commit.body` below the subject line.
  * Indent and format properly (e.g. bullet points preserved).

### Example

```
### 🚀 Features

- 🔀 **Merge branch 'feature/oauth2'** - ([abc1234](...))
    Add OAuth2 login flow with full explanation of scope:
    - why OAuth2 was chosen
    - compatibility with existing login
    - possible future extensions

    - *(auth)* Add login endpoint - ([def5678](...))
    - *(auth)* Implement token exchange - ([ghi9012](...))
    - *(auth)* Add error handling - ([jkl3456](...))
    - *(test)* Add unit tests for OAuth2 flow - ([mno7890](...))
```

---
