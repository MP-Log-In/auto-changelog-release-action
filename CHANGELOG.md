# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

### 🚜 Refactor

- *(action)* Switch version detection to python script output - ([b99055c](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/b99055c5566d13a3619cd4f9b548b117adb4a2f9))

## [1.4.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.4.0..v1.4.1) - 2025-12-26

### 🐛 Bug Fixes

- *(cliff)* Adjust prerelease label placement in compare header - ([f8dee69](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/f8dee69cf3b0641b5a30ae775c41bf450b3a1cb5))

## [1.4.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.3.2..v1.4.0) - 2025-12-26

### 🚀 Features

- *(release)* Support pre-release tagging and changelog rendering - ([5a75231](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/5a7523109f3204e2e5a33037927b2e104eeab67f))

### 🚜 Refactor

- *(scripts)* Rename augment_entry_commits to augment_merge_commits - ([154a95b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/154a95ba2097842073fe545f4ec1c07d3f6ff5ce))

### 🎨 Styling

- *(cliff)* Show commit scope in merge entry template - ([88afb25](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/88afb2530c7078618626ebab835fceddf42376a9))

## [1.3.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.3.1..v1.3.2) - 2025-12-26

### 🐛 Bug Fixes

- *(scripts)* Handle multiple context entries when augmenting commits - ([cd76af2](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/cd76af27bb4ebc10838d48be926b25b26c7e3d7c))

## [1.3.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.3.0..v1.3.1) - 2025-12-23

### 🐛 Bug Fixes

- Reorder and update commit parser rules in config - ([0e7b51e](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/0e7b51e9742b5f548a7c2e9db7e6809e082b9100))

## [1.3.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.8..v1.3.0) - 2025-12-23

### 🚀 Features

- Update commit parser group ordering and skip rules - ([8beb204](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/8beb2042f99e409ca7a1f19f70bbbad1fff83e82))

## [1.2.8](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.7..v1.2.8) - 2025-12-23

### 🐛 Bug Fixes

- *(ci)* Update GITEA_API_URL to use server_url without /api/v1 - ([fc390ce](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/fc390ce048b2d3ef22ca27ab2babd5edb2dce41c))

## [1.2.7](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.6..v1.2.7) - 2025-12-14

### ⚙️ Miscellaneous Tasks

- *(scripts)* Set default git-cliff version to 2.10.1 - ([5cb6dbd](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/5cb6dbddfc37b72fb647d7649aefc59e3dc01345))

## [1.2.4](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.3..v1.2.4) - 2025-12-14

### 🐛 Bug Fixes

- *(config)* Update template to generalize gitea remote and add postprocessors - ([51cfcdc](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/51cfcdc6488c878764193c33121144564e76c802))

## [1.2.3](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.2..v1.2.3) - 2025-11-24

### 🐛 Bug Fixes

- *(ci)* Use ACTION_PATH for git-cliff config generation - ([0646778](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/064677870b9ebac04d2f264fede191205faa0614))

## [1.2.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.1..v1.2.2) - 2025-11-24

### 🐛 Bug Fixes

- *(scripts)* Improve version argument handling in install script - ([e050996](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/e050996fd4d153f59cce0c9483851cae4963908d))

## [1.2.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.2.0..v1.2.1) - 2025-11-24

### 🐛 Bug Fixes

- *(scripts)* Remove redundant output on missing config file - ([ce5cb7b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/ce5cb7bcc0435931a24b017c2fdacf03eb084032))

## [1.2.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.1.0..v1.2.0) - 2025-11-24

### 🚀 Features

- Add templated git-cliff config generation to workflow - ([096ecb5](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/096ecb582296cdd479a32d5eb58512af76621102))
- *(changelog)* Add support for indented commit bodies - ([a83ee3e](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/a83ee3e88f87c3d99368ee1e62f45f4f30dd46c1))

### ⚙️ Miscellaneous Tasks

- *(config)* Adjust formatting and improve changelog parsing - ([d8bf074](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/d8bf0743f7ece328d76a3cde52aac75b1691ada6))

## [1.1.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.0.1..v1.1.0) - 2025-09-29

### 🚀 Features

- *(scripts)* Add type extraction and mismatch detection logic - ([e8426bb](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/e8426bb839dd29f807f232efe5f7bf829ec4f9f1))

### 📚 Documentation

- Add changelog improvement ideas to TODO file - ([f54df9f](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/f54df9fbc42e3fc453042a1f2c36f7cd12e38c41))

### ⚙️ Miscellaneous Tasks

- *(config)* Improve child commit handling in merge template - ([65462f5](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/65462f5a1495aa45afd727a962126db953ab75a5))

## [1.0.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v1.0.0..v1.0.1) - 2025-09-27

### ⚙️ Miscellaneous Tasks

- *(scripts)* Check for existing Python installation - ([94980be](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/94980be3e5e5827b75edf9abeab0987709fa3122))

## [1.0.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.4.3..v1.0.0) - 2025-09-27

### 🚀 Features

- *(ci)* [**breaking**] Enhance changelog generation with context augmentation - ([8de8b47](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/8de8b470386cf9f21cec660ba71d840ea6786231))

### 🐛 Bug Fixes

- *(release)* Fix changelog generation pipe usage - ([fedcc1f](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/fedcc1ff41b9535f5002d046427dd640b647bde4))

### ⚙️ Miscellaneous Tasks

- *(release)* Update action version in workflow - ([73a1b5c](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/73a1b5cc243248b50275b2368a4cd92bbb4a1a8e))
- *(ci)* Allow non-main branch releases - ([121ea5b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/121ea5b57a587626a036738c23e2983380470dd7))

## [0.4.3](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.4.2..v0.4.3) - 2025-06-29

### 🐛 Bug Fixes

- *(script)* Use dynamic branch name for git push - ([27ee174](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/27ee1746dbc7b2c6c1564a04c024337ff158a9c5))

## [0.4.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.4.1..v0.4.2) - 2025-06-29

### 🐛 Bug Fixes

- *(action)* Update conditions for version detection - ([c25b2e9](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/c25b2e9cd551e923b84cd144b818940fd5e1ccff))

## [0.4.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.4.0..v0.4.1) - 2025-06-29

### 🐛 Bug Fixes

- *(action)* Standardize input key naming - ([cbcd5e2](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/cbcd5e2ab7e7f2498021d5043da9999f62dcf44d))

## [0.4.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.6..v0.4.0) - 2025-06-29

### 🚀 Features

- *(action)* Add support for non-main branch releases - ([1d9659b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/1d9659b6df0d63ed17432e677ee77a4c17d2f2f3))

## [0.3.6](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.5..v0.3.6) - 2025-06-29

### ◀️ Revert

- Integrate gha-timer for step timing - ([856565d](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/856565d87f2575d6883705ddde3d177555c1bd86))

## [0.3.5](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.4..v0.3.5) - 2025-06-29

### 🚀 Features

- *(action)* Integrate gha-timer for step timing - ([e5f5084](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/e5f50849316f5dc0b045ac696c3628e610bae695))

### ◀️ Revert

- Improve CI readability with grouped git setup logs - ([039a14a](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/039a14a473493fd74fb61b60910652db3cfd5976))

## [0.3.4](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.2..v0.3.4) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(workflows)* Update action to specific version - ([a4ff409](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/a4ff409fd812a5ccd2291251de5cd2af9bb0e713))
- *(scripts)* Update file permissions to executable - ([374f30a](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/374f30a50206a426b8de7a0b78cde9ad4194469f))

## [0.3.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.1..v0.3.2) - 2025-06-29

### 🚜 Refactor

- *(action)* Simplify script invocation syntax - ([b75e412](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/b75e4121928131c1a1c0cbdea954a4fd602edd1a))

## [0.3.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.3.0..v0.3.1) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(scripts)* Improve CI readability with grouped git setup logs - ([8a3960a](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/8a3960ad8712bc29823dc601a120a61582fa2a3b))

## [0.3.0](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.2.3..v0.3.0) - 2025-06-20

### 🚀 Features

- *(script)* Enhance git-cliff installer with jq support - ([5226899](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/522689977fe8883975e68add1b0cba2e685978ee))

### ⚙️ Miscellaneous Tasks

- *(workflows)* Update release action version - ([79d7c5a](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/79d7c5a7eefda51f03a9bde0e933689c29d57567))

## [0.2.3](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.2.2..v0.2.3) - 2025-06-14

### 🐛 Bug Fixes

- *(script)* Adjust GIT_AUTHOR_DATE format for compatibility - ([5d42ea9](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/5d42ea9ddbfa4f151c83fc16c652d55618f2ee04))

## [0.2.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.2.1..v0.2.2) - 2025-06-14

### 🚀 Features

- *(scripts)* Validate git configuration during setup - ([212e8c6](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/212e8c6a499365ac77c98138a09b6736dec8fe7e))

### 🚜 Refactor

- *(scripts)* Standardize scripts and improve readability - ([041d7e9](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/041d7e9a8a7baa5b6f41ad6dabd7d4837f7d254a))

## [0.2.1](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.1.3..v0.2.1) - 2025-06-14

### 🚀 Features

- *(release)* Add retry logic for release creation - ([29243bd](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/29243bd67344a3020fc3023d238dacbdd96c53ad))

## [0.1.3](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.1.2..v0.1.3) - 2025-06-14

### 🐛 Bug Fixes

- *(workflows)* Configure Git user in major tag creation - ([79921dd](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/79921dd63676138f2cfbcc3894f294b292f0a653))

## [0.1.2](https://git.0xmax42.io/actions/auto-changelog-release-action/compare/v0.1.0..v0.1.2) - 2025-06-14

### 🚀 Features

- *(workflows)* Add workflow to create major version tags - ([9a05866](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/9a0586653a5e7aa6a3acb12d119f4a43c09e96c1))

### ⚙️ Miscellaneous Tasks

- *(workflows)* Update action to main branch - ([043a01c](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/043a01c2bacb78f3c872056f7d18aab4e845a401))
- *(workflows)* Update action version in release workflow - ([9a0d65b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/9a0d65b8eba3d1e06c88bc02f19e2dd5a7d0a731))

## [0.1.0] - 2025-06-14

### 🚀 Features

- *(config)* Update remote repository details in cliff.toml - ([0671495](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/067149548b8c4a522da1504f21a9a6745acc279e))
- *(workflows)* Add token input for release action - ([fcb80ef](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/fcb80ef5ce808537df1e269e203dcd234a4a7657))
- *(action)* Add environment variables for version detection - ([72faeb5](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/72faeb5d9ffbebff0b704d53cb6123c87f65887f))
- *(workflow)* Enhance release process with additional steps - ([7bad547](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/7bad5475390a927f14ed5eccd31c4268dd0d7a28))
- *(action)* Add default values for optional inputs - ([fee52f9](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/fee52f98233ac367dda3d362df1949defd600714))
- *(workflows)* Enhance release process with additional steps - ([4ab6624](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/4ab6624add5de4e52fe2aff373b1a2f22f2557bb))
- *(workflows)* Add automated changelog and release workflow - ([84d0da4](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/84d0da4478cbe6b0ba6d60b3251544ed46597a36))
- *(action)* Add composite action for changelog and release - ([978d002](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/978d002e9eb82247da53ddfb4fa2226527290919))
- *(scripts)* Add CI utilities for versioning and changelog - ([048b964](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/048b96420488bae599ea8f2f7765a2e576b9f718))

### 🐛 Bug Fixes

- *(action)* Ensure fallback for release token input - ([b65e9ee](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/b65e9ee5423a1701ac057a56a09973ed9b2ea7b8))

### 🚜 Refactor

- *(action)* Remove unused steps for version management - ([286d2a6](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/286d2a691683c364025cf0cdd08e4afd60c20356))
- *(action)* Remove unused CLI setup steps - ([209c25d](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/209c25d05a79ec854f9dd49b1da820215e074ba2))
- *(action)* Remove unused changelog and release steps - ([a66fc97](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/a66fc97f2a177b42c93a85bddf969065a849b3a6))

### 🎨 Styling

- *(vscode)* Customize activity bar and theme colors - ([53bad79](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/53bad793ebca739051ba3975aa2628283d3e08ff))

### ⚙️ Miscellaneous Tasks

- *(config)* Add git-cliff configuration for changelog generation - ([e5bddac](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/e5bddac7481a16b43cc81ec115b22c1b13de7425))
- *(workflows)* Update release step with descriptive name - ([e73d132](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/e73d1324b7ea2095ef52512d0c140ef9a11d66f9))
- *(gitignore)* Add rule to exclude environment files - ([14f0a9b](https://git.0xmax42.io/actions/auto-changelog-release-action/commit/14f0a9b4b19e2f981417292a0b844485fbe2018e))


