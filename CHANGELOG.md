# CHANGELOG



## v0.8.1 (2024-05-31)

### Chore

* chore: updated mypy and updated types ([`5524dd7`](https://github.com/Guibod/mightstone/commit/5524dd781ddbc220440b4f3bfa37e693270fe017))

* chore: silenced annoying PytestUnraisableExceptionWarning ([`b7e0bc1`](https://github.com/Guibod/mightstone/commit/b7e0bc1c0a6a21e7d364985a63bb9cc4a132de27))

* chore: applied new black rules to the code ([`8690b52`](https://github.com/Guibod/mightstone/commit/8690b52db051ecae317e693bdd201bc1687524c3))

* chore(deps-dev): bump black from 23.12.1 to 24.3.0

Bumps [black](https://github.com/psf/black) from 23.12.1 to 24.3.0.
- [Release notes](https://github.com/psf/black/releases)
- [Changelog](https://github.com/psf/black/blob/main/CHANGES.md)
- [Commits](https://github.com/psf/black/compare/23.12.1...24.3.0)

---
updated-dependencies:
- dependency-name: black
  dependency-type: direct:development
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`89fc0c1`](https://github.com/Guibod/mightstone/commit/89fc0c14e684016013c1d5734211fda02c2dec04))

* chore(deps-dev): bump pyinstaller from 4.5.1 to 5.13.1

Bumps [pyinstaller](https://github.com/pyinstaller/pyinstaller) from 4.5.1 to 5.13.1.
- [Release notes](https://github.com/pyinstaller/pyinstaller/releases)
- [Changelog](https://github.com/pyinstaller/pyinstaller/blob/develop/doc/CHANGES.rst)
- [Commits](https://github.com/pyinstaller/pyinstaller/compare/v4.5.1...v5.13.1)

---
updated-dependencies:
- dependency-name: pyinstaller
  dependency-type: direct:development
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`3cb34ee`](https://github.com/Guibod/mightstone/commit/3cb34ee6b3cdf71180c6ea8f974353af99714dd7))

* chore: build process lints before tests ([`a0c53d0`](https://github.com/Guibod/mightstone/commit/a0c53d0332de75ef24b2b0b5da9c6471be1be9b8))

* chore(deps): bump pillow from 9.5.0 to 10.3.0

Bumps [pillow](https://github.com/python-pillow/Pillow) from 9.5.0 to 10.3.0.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/9.5.0...10.3.0)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`b9a94f7`](https://github.com/Guibod/mightstone/commit/b9a94f7b5e0e18d9ae1358f1d5d178f3a8451075))

* chore: readme don’t link to another project for issues, centered the logo ([`5ffd878`](https://github.com/Guibod/mightstone/commit/5ffd878f82cff56a3484c732b3d27567cf7f6c58))

### Documentation

* docs: fixed link to issue report ([`eba9be6`](https://github.com/Guibod/mightstone/commit/eba9be627cd6101327f4b112d8052603a22c2838))

### Fix

* fix: custom types are properly deserialed through pydantic 2 ([`0ab6c22`](https://github.com/Guibod/mightstone/commit/0ab6c221d0e8594fd09494fce91fda4d9b69ff60))


## v0.8.0 (2024-05-31)

### Chore

* chore: linting issues ([`d4cc2f9`](https://github.com/Guibod/mightstone/commit/d4cc2f92f1f6b044a17553af2c7412258285c495))

* chore: fixed minor typing issues after mypy upgrade ([`7bf3292`](https://github.com/Guibod/mightstone/commit/7bf329227f4a023a9cffd615d10d9a5ea63e588d))

* chore: upgraded dependency to aiofiles ([`d512acb`](https://github.com/Guibod/mightstone/commit/d512acb2406d8db50de67b6ff16d4c15c648496e))

* chore: remove dependency to aiosqlite ([`3c2de6b`](https://github.com/Guibod/mightstone/commit/3c2de6b54341559b3bfa133ab9b59b5ef6a67609))

* chore: mark project as alpha stage ([`15b4fe4`](https://github.com/Guibod/mightstone/commit/15b4fe45862c556c5c5fe7105a57ca12f497a739))

* chore: upgraded pytest dependency ([`d5cc0b1`](https://github.com/Guibod/mightstone/commit/d5cc0b10ff9ea480d2fc2c15e38bcda8bb90f59a))

* chore: upgraded httpx dependencies ([`5cd4933`](https://github.com/Guibod/mightstone/commit/5cd49331fb40146e1c92ddeb8557da7931ee29bb))

* chore: upgraded all non locked dependencies ([`ec4254c`](https://github.com/Guibod/mightstone/commit/ec4254c01c568cbc9ac0d7cd15beeca05b9b7c79))

### Documentation

* docs: fixed some issue with the configuration doc ([`00e7050`](https://github.com/Guibod/mightstone/commit/00e7050d90362feb2970e4a280b5760c7aec1604))

### Feature

* feat: added logo and enhanced both README and sphinx docs ([`9cd61bc`](https://github.com/Guibod/mightstone/commit/9cd61bc35e69be24e82e356fe326ebe9a991712c))

### Fix

* fix: documentation process at readthedocs. ([`04d0724`](https://github.com/Guibod/mightstone/commit/04d07240272a6623ab72d3752ace1f72f9236ad4))


## v0.7.0 (2024-05-30)

### Chore

* chore: release job uses same context as tests ([`9319f3c`](https://github.com/Guibod/mightstone/commit/9319f3ce0b6833f23d92e62213d47eb79eabcbfa))

### Feature

* feat: cut support for mongita in favor of pymongo_inmemory ([`53e1c4c`](https://github.com/Guibod/mightstone/commit/53e1c4c38a643a589e84884bf39275d64f3c4ad0))

### Test

* test: added tests for python 3.12 ([`190c72f`](https://github.com/Guibod/mightstone/commit/190c72f592436434690236ccabecbd985f9836a9))


## v0.6.4 (2024-05-30)

### Build

* build: ... ([`5c24332`](https://github.com/Guibod/mightstone/commit/5c243329d77fb2830508fa5aacaee31808f14109))

* build: optimized build step

does not depend on test and lint anymore ([`e7d6dbe`](https://github.com/Guibod/mightstone/commit/e7d6dbe20936b3cecda2a13145461d7de860ac89))

### Fix

* fix: mtgjson quick fix for optional retail price. ([`9706323`](https://github.com/Guibod/mightstone/commit/97063238195c90ea20c0888ed786573a90f19d2a))


## v0.6.3 (2023-08-07)

### Build

* build: attempt to resolve build and release.. ([`77234e6`](https://github.com/Guibod/mightstone/commit/77234e662134703912bfb7801eb37b907deddbe0))

### Fix

* fix: integration test for scryfall run a reserve list

This commit intends to generate 0.6.3 release ([`fd41818`](https://github.com/Guibod/mightstone/commit/fd4181829d6b6d993d73dadad1e5745ca88857bc))


## v0.6.2 (2023-08-07)

### Build

* build: attempt to resolve build and release ([`1f29dbc`](https://github.com/Guibod/mightstone/commit/1f29dbce213a4a7c234dc5cd6fff22087dbb22a8))

* build: attempt to resolve build and release ([`af4a208`](https://github.com/Guibod/mightstone/commit/af4a208afe3266ddf830eaed3498a44a3060cb5f))

* build: python semantic release 8, proper setup ([`3f2e5a2`](https://github.com/Guibod/mightstone/commit/3f2e5a27ad3a9e7ccbaffde0f8782176dec168f7))

* build: semantic release fixed to 8.0.4 plus fix in configuration ([`ff8e747`](https://github.com/Guibod/mightstone/commit/ff8e7477c51ae0df8f4f9c99b814bf7a64014e2e))

### Chore

* chore(deps-dev): bump pygments from 2.14.0 to 2.15.0

Bumps [pygments](https://github.com/pygments/pygments) from 2.14.0 to 2.15.0.
- [Release notes](https://github.com/pygments/pygments/releases)
- [Changelog](https://github.com/pygments/pygments/blob/master/CHANGES)
- [Commits](https://github.com/pygments/pygments/compare/2.14.0...2.15.0)

---
updated-dependencies:
- dependency-name: pygments
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`a98abb4`](https://github.com/Guibod/mightstone/commit/a98abb43876ca823198d1e434038a758838c4f61))

* chore(deps): bump certifi from 2022.12.7 to 2023.7.22

Bumps [certifi](https://github.com/certifi/python-certifi) from 2022.12.7 to 2023.7.22.
- [Commits](https://github.com/certifi/python-certifi/compare/2022.12.07...2023.07.22)

---
updated-dependencies:
- dependency-name: certifi
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`3a329ce`](https://github.com/Guibod/mightstone/commit/3a329ceb60349379341343968edb234c8e1de17f))

* chore(deps-dev): bump cryptography from 41.0.0 to 41.0.3

Bumps [cryptography](https://github.com/pyca/cryptography) from 41.0.0 to 41.0.3.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/41.0.0...41.0.3)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`4aa6bd0`](https://github.com/Guibod/mightstone/commit/4aa6bd017239303e998c6dfb3eb3067a65e2bcaf))

* chore(deps): bump requests from 2.28.2 to 2.31.0

Bumps [requests](https://github.com/psf/requests) from 2.28.2 to 2.31.0.
- [Release notes](https://github.com/psf/requests/releases)
- [Changelog](https://github.com/psf/requests/blob/main/HISTORY.md)
- [Commits](https://github.com/psf/requests/compare/v2.28.2...v2.31.0)

---
updated-dependencies:
- dependency-name: requests
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`da290cb`](https://github.com/Guibod/mightstone/commit/da290cb5c7cba99dc90d055a5e74d63380286402))

* chore(deps): bump cryptography from 40.0.1 to 41.0.0

Bumps [cryptography](https://github.com/pyca/cryptography) from 40.0.1 to 41.0.0.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/40.0.1...41.0.0)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`c1f9efb`](https://github.com/Guibod/mightstone/commit/c1f9efb4856f0bb43a6956138efd631fbe66b12c))

### Fix

* fix: applied up-to-date mtgjson v5.2.1 schema

mtgjson rulings are now optional in cards (Set, Face, and Deck) ([`41cbb5f`](https://github.com/Guibod/mightstone/commit/41cbb5f1c3bb4721327404b7f4125712a1c336a3))

* fix: applied updated card conjurer template

- metadata is removed
- name is part of root object ([`9980b4b`](https://github.com/Guibod/mightstone/commit/9980b4b73360745d3af1fe267f4cfa794a01b8b6))

* fix: scryfall random endpoint don’t use local cache anymore ([`7bb6012`](https://github.com/Guibod/mightstone/commit/7bb601206ab3a6a453efc2c0a9167f0c893c59a5))

* fix: synchronized functions that return generators are fixed ([`fe14af1`](https://github.com/Guibod/mightstone/commit/fe14af1d47500a3b38a206d7513a16a3d7ac0cb6))


## v0.6.1 (2023-04-01)

### Fix

* fix: release script should not fail anymore on the lack of mypy types during the lint step ([`7401671`](https://github.com/Guibod/mightstone/commit/740167141bcc637202808794f47eaef57abad8a9))


## v0.6.0 (2023-04-01)

### Chore

* chore: complete mypy coverage and the build is greenwip ([`06bb7ab`](https://github.com/Guibod/mightstone/commit/06bb7abe6221c359b91f68bf733fd4d492b48342))

* chore: gitignored .python-version file ([`e932078`](https://github.com/Guibod/mightstone/commit/e93207813ed30ce6a1e2f36788822a167ad9028d))

### Feature

* feat: persistence support ([`24db834`](https://github.com/Guibod/mightstone/commit/24db83426fd4a203f0759cd06a13350079b176e5))

### Fix

* fix: our mongita fork allow usage of motor 3.1.1 that enables support for python 3.11 ([`4a0738f`](https://github.com/Guibod/mightstone/commit/4a0738f2b89a49ede4f522b5d8800dcb78eda8a2))


## v0.5.0 (2023-03-07)

### Chore

* chore: introducing synchronize() function that will provide sync version of async features ([`6edf5bc`](https://github.com/Guibod/mightstone/commit/6edf5bcc69e3c3b5b98e1f6a366bab84f3ee45fe))

* chore: added dependency to asgiref that is a reference in term of async_to_sync ([`fccdd40`](https://github.com/Guibod/mightstone/commit/fccdd40178353f696ba5a8570ae904e3fe6d59bc))

* chore: Rule framework now use RuleExplorer a MightstoneHttpClient

Removed dependency to Requests, and is async ready. ([`0d899b0`](https://github.com/Guibod/mightstone/commit/0d899b011d7d0ab904a846d834f0f71933d73df5))

* chore: silenced tests in CI for integration tests that rely on real connection to third part API ([`02047af`](https://github.com/Guibod/mightstone/commit/02047af425e98708a06c7fd09cf8b0c1add2dc3b))

* chore: type hinting some of async library of mightstone ([`44639fd`](https://github.com/Guibod/mightstone/commit/44639fdf61f64d905053c047731a057f7526e3bb))

### Documentation

* docs: added proper scryfall documentation ([`b17cd2b`](https://github.com/Guibod/mightstone/commit/b17cd2bca2f3ec69075ff2fa55a716124a180bc6))

### Feature

* feat: normalized async lib, aiostream is out, asynclibstd is the new norm

Also added documentation, and many other important improvement
I’ve still failed to silence pytest PytestUnraisableExceptionWarning for MtgJSON implementation that will need to be rewritten. :/ ([`ea76a8e`](https://github.com/Guibod/mightstone/commit/ea76a8e9461b4b73039d3b39831975ab8e09503e))

* feat: mtgjson services applies the new method() / method_async() dichotomy ([`d407077`](https://github.com/Guibod/mightstone/commit/d40707770b50aef01026fe37605ba2bd1fddb2dc))

* feat: card-conjurer services applies the new method() / method_async() dichotomy ([`e7dfb06`](https://github.com/Guibod/mightstone/commit/e7dfb06f42817ed364cae27da1e9abf879490b9f))

* feat: edhrec services applies the new method() / method_async() dichotomy ([`6e0e165`](https://github.com/Guibod/mightstone/commit/6e0e1659a1ea551039793643986d9f40cc7129f9))

* feat: scryfall services applies the new method() / method_async() dichotomy ([`d82bed1`](https://github.com/Guibod/mightstone/commit/d82bed1de264658cd3dfde025e96d48983cb725a))

* feat: moved rules to the wotc service, introducing the first api with both sync/async functions ([`8ceb49d`](https://github.com/Guibod/mightstone/commit/8ceb49d8cc1ea1e54f991b809717f4fbe5b81176))

* feat: moved rules to the wotc service, introducing the first api with both sync/async functions ([`1acd5a7`](https://github.com/Guibod/mightstone/commit/1acd5a71a41b3cca8bc295fb5cb20033ecc21157))

### Fix

* fix: MightstoneHttpClient will not reuse client anymore

this is due to big issue while trying to run consecutive call over different asyncio loops, this is a nightmare so F that and move as suggested in this HTTPX issue: https://github.com/encode/httpx/issues/2473 ([`05d3336`](https://github.com/Guibod/mightstone/commit/05d333620b506a7d05d74a8d3a7b9757800a5ecf))

* fix: scryfall supports httpx now, also added a bunch of integration tests ([`ef3b51b`](https://github.com/Guibod/mightstone/commit/ef3b51bcea71d714d3effdb0e54b424202d34062))


## v0.4.0 (2023-02-26)

### Chore

* chore: silenced an error related to uncatched generator early exit ([`781dc0e`](https://github.com/Guibod/mightstone/commit/781dc0ee232e52da1b3534a6f5fa0f74a09db1fd))

* chore: silenced a warning about skip tests ([`c552af1`](https://github.com/Guibod/mightstone/commit/c552af16a816598ac15ec6c644ccb03bc00a9c36))

* chore: removed dependency to aiohttp ([`da88a68`](https://github.com/Guibod/mightstone/commit/da88a680f7504d1aec2cdf231e932045a880ff48))

### Feature

* feat: added support for inline icons in card conjurer ([`bbefa6b`](https://github.com/Guibod/mightstone/commit/bbefa6bf6cb8cfd2c22969496a6069506591b2be))

### Fix

* fix: restoring support for card conjurer ([`f97b523`](https://github.com/Guibod/mightstone/commit/f97b523980184afad820117a271704527821e2ca))

### Refactor

* refactor: introducing dependency injector and switched from aiohttp to httpx client ([`1ade77a`](https://github.com/Guibod/mightstone/commit/1ade77a64bdf6f30e622b5b54378acada2f8553d))

* refactor: async_file_obj support async iterator ([`f5ed7dc`](https://github.com/Guibod/mightstone/commit/f5ed7dc9e65dca441ae5c9e63e674347ab2d583d))

### Unknown

* . ([`756bc03`](https://github.com/Guibod/mightstone/commit/756bc03f1b1086938c0780c9ed436585313447d2))


## v0.3.0 (2023-02-19)

### Chore

* chore: added OpenSSF best practices tag ([`9423a7f`](https://github.com/Guibod/mightstone/commit/9423a7f08a972d9be95738af09a5a8b199108c22))

### Feature

* feat: added CardConjurer support

Cardconjurer is a generic card editor that can support MTG pretty well.

Changes:
 - Added Model entities
 - Added CLI to parse and render a card ([`d96babf`](https://github.com/Guibod/mightstone/commit/d96babf33a57d280efee9d96a4f26fd195c70a90))


## v0.2.2 (2023-02-17)

### Chore

* chore: removed some tags for third part dependency that we don’t wish to use ([`f1a27cd`](https://github.com/Guibod/mightstone/commit/f1a27cd63cfe5897d9025a0446630c6b058bbd77))

### Fix

* fix: attempt to fix CI release by using deep checkout instead of shallow checkout ([`e79b94c`](https://github.com/Guibod/mightstone/commit/e79b94ca17f1c12be8bff2a43bc2807f1f435336))


## v0.2.1 (2023-02-17)

### Chore

* chore: explicitly added requests as a dependency

it is use in Rule classes ([`ceb8323`](https://github.com/Guibod/mightstone/commit/ceb8323f372b3f348abdf9ba99be4a892e8dc4ef))

* chore: reorganized pyproject.toml

- docs
- release
- dev

groups ([`d0c77b9`](https://github.com/Guibod/mightstone/commit/d0c77b9994038b4ef0a8a58b04e1a6150478ddce))

### Fix

* fix: switched back from npm semantic-release to python-semantic-release ([`7b09e76`](https://github.com/Guibod/mightstone/commit/7b09e7670341d89ea4689be605f4b097130579f6))

* fix: read the doc configuration uses a properly prepared environment ([`b3ec459`](https://github.com/Guibod/mightstone/commit/b3ec459d6853b83912c4b3da9a7362badab3baaf))


## v0.2.0 (2023-02-17)

### Chore

* chore: ignore flake8 trailing whitespace of doom ([`3a1fb09`](https://github.com/Guibod/mightstone/commit/3a1fb09508958ef81661463dacc53e2dd4317d6c))

* chore: added new dependencies to the project ([`380678b`](https://github.com/Guibod/mightstone/commit/380678b378cda2990c857676f82c0572e81df726))

* chore: deleted some useless files ([`0fafdfb`](https://github.com/Guibod/mightstone/commit/0fafdfbf080f491c9c0bc27e233726e426e1b612))

* chore: root logger defined ([`08a2c02`](https://github.com/Guibod/mightstone/commit/08a2c02f1a7bfc3854f22f88e900de1d7f29f3b5))

* chore: refactored cli commands to be defined in each service module ([`35d721d`](https://github.com/Guibod/mightstone/commit/35d721d6433bc311eb52a36bb387384a42376e58))

* chore: added async compressed stream reader/writer ([`91cdd94`](https://github.com/Guibod/mightstone/commit/91cdd94f73bf1bdf6bcfe39512c451f10535fd57))

* chore: moved back to semantic release job

See: https://github.com/bjoluc/semantic-release-config-poetry ([`4f502b8`](https://github.com/Guibod/mightstone/commit/4f502b875504a7e18c88cc3595c4dae8738c4be8))

### Feature

* feat: mtgjson api is tested ([`c4a6dff`](https://github.com/Guibod/mightstone/commit/c4a6dff493ea87e1426450680d4689ed69aabf0e))

* feat: mtgjson model and api ([`9ab63eb`](https://github.com/Guibod/mightstone/commit/9ab63ebc0a9afa628b6c6392baea285afde7924d))

* feat: added diff support for comprehensive rules

Along side with a RuleRef.prev() and an explore() method to search previous rules ([`5f81186`](https://github.com/Guibod/mightstone/commit/5f81186e35b95e78b176b032206e6e26dd1e1bdd))

### Fix

* fix: release process with semantic release is now working (at least locally) ([`f3c7bdc`](https://github.com/Guibod/mightstone/commit/f3c7bdcfcb55086219c7121b152251358a554399))

* fix: attempt to change semantic release version variable ([`a939b59`](https://github.com/Guibod/mightstone/commit/a939b59dcd4df4d66e55c18f85b3d9305ec3edb2))

* fix: restored documentation generation ([`16ac1e4`](https://github.com/Guibod/mightstone/commit/16ac1e469b1671172d9a79872a1c845a1e7bc607))

### Unknown

* doc: mtgjson documentation is ok, overhauled documentation in general ([`9e5540a`](https://github.com/Guibod/mightstone/commit/9e5540a96d5135638645de14d0fd8bec86533813))

* doc: added a note regarding YAJL and ijson ([`eefc43a`](https://github.com/Guibod/mightstone/commit/eefc43a07cff8d7457eec5c4b6f3f77c2d707a65))


## v0.1.3 (2023-02-05)

### Documentation

* docs: minor change in documentation ([`ba3bc8a`](https://github.com/Guibod/mightstone/commit/ba3bc8afd309cfe07dc46df05ebc9bd9346f18c2))

### Fix

* fix: a fake commit to validate release process ([`6f20701`](https://github.com/Guibod/mightstone/commit/6f207011b4b6795f29d0e7eb2433fbaeaf12cffd))

* fix: changed build command for semantic-release ([`d96e0b4`](https://github.com/Guibod/mightstone/commit/d96e0b4e12c28af853224598261a38ccbbdaae17))


## v0.1.1 (2023-02-05)

### Fix

* fix: changed build command for semantic-release ([`81784d8`](https://github.com/Guibod/mightstone/commit/81784d89d714ee95220ba59f64f2139674620243))


## v0.1.0 (2023-02-05)

### Chore

* chore: cleanup by removing doc Makefile and gitignore third part template ([`fbc9cb4`](https://github.com/Guibod/mightstone/commit/fbc9cb4e98a5155fd78ad08d82f7da23d85ff6ce))

* chore: removed VS code configuration and gitignored it ([`e56b22a`](https://github.com/Guibod/mightstone/commit/e56b22a7e8e926ade842a527934bceaa274ce1b7))

* chore: removed useless gitlab ci support file ([`17c2460`](https://github.com/Guibod/mightstone/commit/17c2460c587f4a034f12a4ea9a4a1a46cb578481))

* chore: removed bumpversions leftover file ([`05ca220`](https://github.com/Guibod/mightstone/commit/05ca2205bf42ac7e4bde9a7b151b4e4a439c9887))

* chore: added missing dependency to aiostream ([`ecd0e0b`](https://github.com/Guibod/mightstone/commit/ecd0e0b1c00aab26b271b6a9892872bd9e4cf067))

* chore: reseted version to 0.0.0, and switched to python-semantic-release ([`e381eca`](https://github.com/Guibod/mightstone/commit/e381eca26eec460c9c496155735348d45333c7ad))

* chore: removed support for python 3.8 in tests ([`dbcb11f`](https://github.com/Guibod/mightstone/commit/dbcb11f723fb185c11cc25923089914ddf5cca0b))

* chore: ._* files are gitignored ([`2e9b980`](https://github.com/Guibod/mightstone/commit/2e9b980b269abf9b952d1e4a0e2f61abe9fab5c9))

* chore: trying to work on version tagging ([`4a67efb`](https://github.com/Guibod/mightstone/commit/4a67efb660f9bde4bd42d2f34fc51a9e8fa96785))

* chore: added support for read the docs / sphinx documentation ([`323f234`](https://github.com/Guibod/mightstone/commit/323f23450d2a129ad4e7ee5a328d2500189a849d))

* chore: upgraded CI dependency from actions/setup-python@v3 to actions/setup-python@v4 ([`e29898b`](https://github.com/Guibod/mightstone/commit/e29898bfe8929000d71ae7ff9e1762a2555097d5))

* chore: rule color support ([`996550b`](https://github.com/Guibod/mightstone/commit/996550b393e6f766f6a56dfd19f72a46e383e689))

* chore: initialized the project using cookiecutter poetry ([`c390776`](https://github.com/Guibod/mightstone/commit/c3907764a9fd5287d643938f4b638680857ee8d3))

### Feature

* feat: added ComprehensiveRules support ([`2faefa7`](https://github.com/Guibod/mightstone/commit/2faefa72017c403024f93f3b76aa2d12360481ac))

* feat: added missing CLI for scryfall set ([`f2da907`](https://github.com/Guibod/mightstone/commit/f2da907271670da6965658fe1b9e209ee1ada8d2))

* feat: a quick check on documentation ([`73ec14b`](https://github.com/Guibod/mightstone/commit/73ec14bda4266e62bdc2e4a40f2f393b98eb4e56))

* feat: added complete scryfall api and cli functions ([`6781302`](https://github.com/Guibod/mightstone/commit/67813021b631c4452b60c84de5dd6997817ecb97))

* feat: added all cli commands for static edhrec, ([`f522214`](https://github.com/Guibod/mightstone/commit/f522214b557ece3e12b774022162560395cf4abe))

* feat: added two sample cli commands for edhrec ([`8d6b2ed`](https://github.com/Guibod/mightstone/commit/8d6b2ed7f20a4a08e731c16792576e071832ae48))

* feat: added support for edhrec recs ([`8dc5601`](https://github.com/Guibod/mightstone/commit/8dc560151ae913e4f8af7b0d52cbbc2b1db80177))

* feat: edhrec has support for all static pages and to filter endpoint ([`1a8c8cf`](https://github.com/Guibod/mightstone/commit/1a8c8cfc13b459b7fd5286a100faf5a60200be6c))

### Fix

* fix: enable semantic release on main branch instead of master branch ([`9b5ce98`](https://github.com/Guibod/mightstone/commit/9b5ce986cb55d839de90969ddf60c2916bb108cb))

### Unknown

* Bump version: 0.0.1 → 0.0.2 ([`2239133`](https://github.com/Guibod/mightstone/commit/2239133ede8af608805c3f64d6fc1d91ccff88a5))

* Initial commit ([`19d5bed`](https://github.com/Guibod/mightstone/commit/19d5bedb7a91f83cd9a2208ca9386d04b452f27f))
