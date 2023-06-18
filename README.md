## Environments

- [Web (prod)](https://terakoyaweb.com/)
- [Web (dev)](https://dev.terakoyaweb.com/)

## TODO

- First, [run command](https://linuxfan.info/post-1486) `bash init.sh` to initialize the project (ex: package installation etc.)

- Update .env file contents to Github Action's secrets when local .env changes

## AWS boto3 intellisense

- Run command pallete ">AWS boto3: Auto-discover boto3 services in current project" to [enable intellisense for boto3](https://dev.classmethod.jp/articles/try-boto3-stubs/)

## Test

- A test file must be named with the prefix "test_" or suffix "_test" to [be discovered by pytest](https://www.tutorialspoint.com/pytest/pytest_identifying_test_files_and_functions.htm).

- Test cases should be [black box tests](https://shiftasia.com/ja/column/%E3%83%96%E3%83%A9%E3%83%83%E3%82%AF%E3%83%9C%E3%83%83%E3%82%AF%E3%82%B9%E3%83%86%E3%82%B9%E3%83%88%E3%81%A8%E3%81%AF/) only without white box tests as much as possible to [reduce the costs of creating and maintaining a test case](https://www.javatpoint.com/advantages-and-dsadvantages-of-black-box-testing).

## OpenAPI (Swagger)

- Execute openapi/make_openapi_spec.py to generate openapi.yml replacing environment variables with actual values loaded from .env file

- Open openapi.yml and execute command pallete ">Swagger UI: Preview current file" to [preview the API spec in web browser](https://marketplace.visualstudio.com/items?itemName=Arjun.swagger-viewer)

## uvicorn

- Run command `uvicorn functions.hub:app --reload` (--reload: auto-reload when code changes) to [run the app in development mode](https://fastapi.tiangolo.com/tutorial/first-steps/)

- Open `http://localhost:8000/docs` in browser to [view the API spec in OpenAPI](https://fastapi.tiangolo.com/tutorial/first-steps/#interactive-api-docs)

- Open `http://localhost:8000/redoc` in browser to [view the API spec in ReDoc](https://fastapi.tiangolo.com/tutorial/first-steps/#alternative-api-docs)

## Set a secret for GitHub Actions

1. `gh auth login`
2. `gh secret set ENV_FILE_CONTENTS -b "$(cat .env)"`

- https://cli.github.com/manual/gh_secret_set
- https://github.com/cli/cli/pull/4534
