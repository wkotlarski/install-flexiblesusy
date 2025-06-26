# Script to install FlexibleSUSY

## Introduction
[FlexibleSUSY](https://github.com/FlexibleSUSY/FlexibleSUSY) relias on some and optionally can link to certain external libraries.
While this allows to use the state-of-the-art computations provided by these libraries and avoid mistakes caused by providing our own functions for doing, for example, basic matrix manipulations it also means that its instalation is not so straightword.

This script helps installing FlexibleSUSY on Linux.

## Usage
Example use
```
python3 install.py SM,MSSM
```
The last argument is a `,`-separated list of models you'd like to configure FlexibleSUSY with.

## Dependencies

The script can automatically install following external dependencies

- [GM2Calc](https://github.com/GM2Calc/GM2Calc)
- [Himalaya](https://github.com/Himalaya-Library/Himalaya)
- [HiggsTools](https://gitlab.com/higgsbounds/higgstools)
- [COLLIER](https://collier.hepforge.org)
- [LoopTools](https://feynarts.de/looptools)

Additionally, it can install following system dependencies (although we recommend that a user installs them usings system's package manager)

- Boost
- GSL

## Getting help
If the script doesn't work for you, please create an [Issue](https://github.com/wkotlarski/install-flexiblesusy/issues)
