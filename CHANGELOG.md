# Changelog

<!--next-version-placeholder-->

## v0.6.1 (2023-04-01)
### Fix
* Release script should not fail anymore on the lack of mypy types during the lint step ([`7401671`](https://github.com/Guibod/mightstone/commit/740167141bcc637202808794f47eaef57abad8a9))

## v0.6.0 (2023-04-01)
### Feature
* Persistence support ([`24db834`](https://github.com/Guibod/mightstone/commit/24db83426fd4a203f0759cd06a13350079b176e5))

### Fix
* Our mongita fork allow usage of motor 3.1.1 that enables support for python 3.11 ([`4a0738f`](https://github.com/Guibod/mightstone/commit/4a0738f2b89a49ede4f522b5d8800dcb78eda8a2))

## v0.5.0 (2023-03-07)
### Feature
* Normalized async lib, aiostream is out, asynclibstd is the new norm ([`ea76a8e`](https://github.com/Guibod/mightstone/commit/ea76a8e9461b4b73039d3b39831975ab8e09503e))
* Mtgjson services applies the new method() / method_async() dichotomy ([`d407077`](https://github.com/Guibod/mightstone/commit/d40707770b50aef01026fe37605ba2bd1fddb2dc))
* Card-conjurer services applies the new method() / method_async() dichotomy ([`e7dfb06`](https://github.com/Guibod/mightstone/commit/e7dfb06f42817ed364cae27da1e9abf879490b9f))
* Edhrec services applies the new method() / method_async() dichotomy ([`6e0e165`](https://github.com/Guibod/mightstone/commit/6e0e1659a1ea551039793643986d9f40cc7129f9))
* Scryfall services applies the new method() / method_async() dichotomy ([`d82bed1`](https://github.com/Guibod/mightstone/commit/d82bed1de264658cd3dfde025e96d48983cb725a))
* Moved rules to the wotc service, introducing the first api with both sync/async functions ([`8ceb49d`](https://github.com/Guibod/mightstone/commit/8ceb49d8cc1ea1e54f991b809717f4fbe5b81176))
* Moved rules to the wotc service, introducing the first api with both sync/async functions ([`1acd5a7`](https://github.com/Guibod/mightstone/commit/1acd5a71a41b3cca8bc295fb5cb20033ecc21157))

### Fix
* MightstoneHttpClient will not reuse client anymore ([`05d3336`](https://github.com/Guibod/mightstone/commit/05d333620b506a7d05d74a8d3a7b9757800a5ecf))
* Scryfall supports httpx now, also added a bunch of integration tests ([`ef3b51b`](https://github.com/Guibod/mightstone/commit/ef3b51bcea71d714d3effdb0e54b424202d34062))

### Documentation
* Added proper scryfall documentation ([`b17cd2b`](https://github.com/Guibod/mightstone/commit/b17cd2bca2f3ec69075ff2fa55a716124a180bc6))

## v0.4.0 (2023-02-26)
### Feature
* Added support for inline icons in card conjurer ([`bbefa6b`](https://github.com/Guibod/mightstone/commit/bbefa6bf6cb8cfd2c22969496a6069506591b2be))

### Fix
* Restoring support for card conjurer ([`f97b523`](https://github.com/Guibod/mightstone/commit/f97b523980184afad820117a271704527821e2ca))

## v0.3.0 (2023-02-19)
### Feature
* Added CardConjurer support ([`d96babf`](https://github.com/Guibod/mightstone/commit/d96babf33a57d280efee9d96a4f26fd195c70a90))

## v0.2.2 (2023-02-17)
### Fix
* Attempt to fix CI release by using deep checkout instead of shallow checkout ([`e79b94c`](https://github.com/Guibod/mightstone/commit/e79b94ca17f1c12be8bff2a43bc2807f1f435336))

## v0.2.1 (2023-02-17)
### Fix
* Switched back from npm semantic-release to python-semantic-release ([`7b09e76`](https://github.com/Guibod/mightstone/commit/7b09e7670341d89ea4689be605f4b097130579f6))
* Read the doc configuration uses a properly prepared environment ([`b3ec459`](https://github.com/Guibod/mightstone/commit/b3ec459d6853b83912c4b3da9a7362badab3baaf))

## v0.2.0 (2023-02-17)
### Feature
* Mtgjson api is tested ([`c4a6dff`](https://github.com/Guibod/mightstone/commit/c4a6dff493ea87e1426450680d4689ed69aabf0e))
* Mtgjson model and api ([`9ab63eb`](https://github.com/Guibod/mightstone/commit/9ab63ebc0a9afa628b6c6392baea285afde7924d))
* Added diff support for comprehensive rules ([`5f81186`](https://github.com/Guibod/mightstone/commit/5f81186e35b95e78b176b032206e6e26dd1e1bdd))

### Fix
* Release process with semantic release is now working (at least locally) ([`f3c7bdc`](https://github.com/Guibod/mightstone/commit/f3c7bdcfcb55086219c7121b152251358a554399))
* Attempt to change semantic release version variable ([`a939b59`](https://github.com/Guibod/mightstone/commit/a939b59dcd4df4d66e55c18f85b3d9305ec3edb2))
* Restored documentation generation ([`16ac1e4`](https://github.com/Guibod/mightstone/commit/16ac1e469b1671172d9a79872a1c845a1e7bc607))

## v0.1.3 (2023-02-05)
### Fix
* A fake commit to validate release process ([`6f20701`](https://github.com/Guibod/mightstone/commit/6f207011b4b6795f29d0e7eb2433fbaeaf12cffd))

### Documentation
* Minor change in documentation ([`ba3bc8a`](https://github.com/Guibod/mightstone/commit/ba3bc8afd309cfe07dc46df05ebc9bd9346f18c2))

## v0.1.2 (2023-02-05)
### Fix
* Changed build command for semantic-release ([`d96e0b4`](https://github.com/Guibod/mightstone/commit/d96e0b4e12c28af853224598261a38ccbbdaae17))

## v0.1.1 (2023-02-05)
### Fix
* Changed build command for semantic-release ([`81784d8`](https://github.com/Guibod/mightstone/commit/81784d89d714ee95220ba59f64f2139674620243))

## v0.1.0 (2023-02-05)
### Feature
* Added ComprehensiveRules support ([`2faefa7`](https://github.com/Guibod/mightstone/commit/2faefa72017c403024f93f3b76aa2d12360481ac))
* Added missing CLI for scryfall set ([`f2da907`](https://github.com/Guibod/mightstone/commit/f2da907271670da6965658fe1b9e209ee1ada8d2))
* A quick check on documentation ([`73ec14b`](https://github.com/Guibod/mightstone/commit/73ec14bda4266e62bdc2e4a40f2f393b98eb4e56))
* Added complete scryfall api and cli functions ([`6781302`](https://github.com/Guibod/mightstone/commit/67813021b631c4452b60c84de5dd6997817ecb97))
* Added all cli commands for static edhrec, ([`f522214`](https://github.com/Guibod/mightstone/commit/f522214b557ece3e12b774022162560395cf4abe))
* Added two sample cli commands for edhrec ([`8d6b2ed`](https://github.com/Guibod/mightstone/commit/8d6b2ed7f20a4a08e731c16792576e071832ae48))
* Added support for edhrec recs ([`8dc5601`](https://github.com/Guibod/mightstone/commit/8dc560151ae913e4f8af7b0d52cbbc2b1db80177))
* Edhrec has support for all static pages and to filter endpoint ([`1a8c8cf`](https://github.com/Guibod/mightstone/commit/1a8c8cfc13b459b7fd5286a100faf5a60200be6c))

### Fix
* Enable semantic release on main branch instead of master branch ([`9b5ce98`](https://github.com/Guibod/mightstone/commit/9b5ce986cb55d839de90969ddf60c2916bb108cb))
