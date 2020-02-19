# Development

## Publish a version of the library
You need to create a new release on GitHub to trigger travis-ci

## Webapp bundling
* The library, when published, is bundled with a fixed version of [broccoli-web](https://github.com/broccoli-platform/broccoli-web)
* This is done by
    * `broccoli-web` publishes its built artifacts by uploading them as GitHub release assets
    * Fix a `broccoli-web` version in `setup.py`
    * When publishing, `sdist` is run. We override it so that `sdist` additionally pulls the GitHub release asset of the fixed `broccoli-web` version and populates it to the `web` folder
    * When the actual `sdist` is run, we explicitly instruct it to include the `web` folder
        * This is "very apparently" controlled by `MANIFEST.in`
    * When a user pulls the `broccoli-server` library, `bdist` is run. We explicitly instruct it to **not omit** the `web` folder
        * This is "very apparently" controlled by `include_package_data` and `package_data` in `setup.py`
