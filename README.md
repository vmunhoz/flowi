# Flowi

![Build Status](https://github.com/psilva-leo/flowi/actions/workflows/build.yml/badge.svg) [![codecov](https://codecov.io/gh/psilva-leo/flowi/branch/master/graph/badge.svg?token=BTJ776QRUJ)](https://codecov.io/gh/psilva-leo/flowi)

Flowi is a component based ML lifecycle platform that empowers data scientists to bring their knowledge to the model with built-in
scalability, experiment tracking, deploy, monitoring and parameter optimization.

## Development
Useful commands for development

### Bump Version
Using Bum2version specifying major, minor or patch.
``
bump2version patch
``

### Pre-commit
``
pre-commit run --all-files
``

### Publish

Building package
``
poetry build
``

Publishing version
``
poetry publish
``
