import os
import importlib


def show_layer_packages_on_lambda():
    """
    Layer's packages are installed in /opt directory on AWS Lambda execution environment.
    https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/invocation-layers.html#invocation-layers-accessing
    """
    print("Testing importability of packages in /opt:")
    for name in os.listdir('/opt'):
        try:
            importlib.import_module(name)
            print(f"{name} is importable")
        except ImportError:
            print(f"{name} is not importable")
