## TODO

- Update .env file contents to Github Action's secrets when local .env changes

## AWS boto3 intellisense

- Execute command pallete ">AWS boto3: Auto-discover boto3 services in current project" to [enable intellisense for boto3](https://dev.classmethod.jp/articles/try-boto3-stubs/)

## Test

- A test file must be named with the prefix "test_" or suffix "_test" to [be discovered by pytest](https://www.tutorialspoint.com/pytest/pytest_identifying_test_files_and_functions.htm).

- Test cases should be [black box tests](https://shiftasia.com/ja/column/%E3%83%96%E3%83%A9%E3%83%83%E3%82%AF%E3%83%9C%E3%83%83%E3%82%AF%E3%82%B9%E3%83%86%E3%82%B9%E3%83%88%E3%81%A8%E3%81%AF/) only without white box tests as much as possible to [reduce the costs of creating and maintaining a test case](https://www.javatpoint.com/advantages-and-dsadvantages-of-black-box-testing).

## OpenAPI(Swagger)

- Execute openapi/make_openapi_spec.py to generate openapi.yml replacing environment variables with actual values loaded from .env file

- Open openapi.yml and execute command pallete ">Swagger UI: Preview current file" to [preview the API spec in web browser](https://marketplace.visualstudio.com/items?itemName=Arjun.swagger-viewer)
