## TODO
- Update .env file contents to Github Action's secrets when local .env changes

- Execute command pallete ">AWS boto3: Auto-discover boto3 services in current project" to [enable intellisense for boto3](https://dev.classmethod.jp/articles/try-boto3-stubs/)

<!-- - Execute command pallete ">Python: Configure Tests" to enable pytest -->

<!-- - Execute command pallete ">AWS: Connect to AWS" to [connect to AWS using AWS Toolkit extension](https://dev.classmethod.jp/articles/aws-toolkit-for-vs-code-sync-s3-bucket-locally-and-perform-crud-operations-on-objects-from-vs-code/) -->

## Test

- A test file must be named with the prefix "test_" or suffix "_test" [to be discovered by pytest](https://www.tutorialspoint.com/pytest/pytest_identifying_test_files_and_functions.htm).

- Test cases should be [black box tests](https://shiftasia.com/ja/column/%E3%83%96%E3%83%A9%E3%83%83%E3%82%AF%E3%83%9C%E3%83%83%E3%82%AF%E3%82%B9%E3%83%86%E3%82%B9%E3%83%88%E3%81%A8%E3%81%AF/) only without white box tests as much as possible [to reduce the costs of creating and maintaining a test case](https://www.javatpoint.com/advantages-and-dsadvantages-of-black-box-testing).