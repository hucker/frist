## Running Tests in Parallel

This project supports running tests in parallel using [pytest-xdist](https://pypi.org/project/pytest-xdist/).

To run tests in parallel (using all available CPU cores):

```
pytest -n auto
```

Or specify the number of workers:

```
pytest -n 4
```

This requires the `pytest-xdist` plugin, which is included in the development dependencies.
