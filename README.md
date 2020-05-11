# Python DI / IoC container

> Dependency injection means giving an object its instance variables.
>
> -- [James Shore, Dependency Injection Demystified](http://jamesshore.com/Blog/Dependency-Injection-Demystified.html)

Initially it was created for AWS Lambda Functions to simplify development
with loose coupling component and improved testing capabilities.

Inspiration comes from [python:design_patterns:inversion_of_control](https://web.archive.org/web/20130703221553/http://www.emilmont.net/doku.php?id=python:design_patterns:inversion_of_control) summary article.

This modules is an optimized version of a container used in [p3.4.advanced-di-ioc](https://github.com/jaymecd/lambda-modular-python/tree/master/p3.4.advanced-di-ioc/myfunction/src/di) section of my [lambda-modular-python](https://github.com/jaymecd/lambda-modular-python) MOB session @cloudreach.

## Usage

Orchestrate container in `ioc.py` file:

```python
# ioc.py
import pydioc
import boto3
import some_sdk
from . import services

def build_container(ssm_param_api_key: str, ddb_status_table: str, format_type: str) -> pydioc.Container:
    return pydioc.Container(
        ("_boto3_session", boto3.Session),
        ("lambda_context", pydioc.ContextProxy),

        ("_api_key_loader", services.api_key_loader, ["_boto3_session", lambda: ssm_param_api_key]),
        ("_status_updater", services.status_updater, ["_boto3_session", "lambda_context", lambda: ddb_status_table]),

        ("_sdk_data_formatter", some_sdk.FormatterFactory, [lambda: format_type]),
        ("_sdk_client_factory", services.sdk_client_factory, ["_api_key_loader"]),

        ("_sdk_data_transfer", services.sdk_data_transfer, ["_sdk_client_factory", "_sdk_data_formatter", "lambda_context"]),

        ("event_handler", services.event_handler, ["_sdk_data_transfer", "_status_updater"]),
    )
```

Define services in `services.py` file:

```python
# services.py
import boto3
import some_sdk

# ...

def api_key_loader(session: boto3.Session, ssm_param_api_key: str):
    assert ssm_param_api_key, 'expecting non empty api_key param'

    def _api_key_loader():
        # very simplified code
        return session.client('ssm').get_parameter(Name=ssm_param_api_key)["Parameter"]["Value"]

    return _api_key_loader

def sdk_client_factory(load_api_key: api_key_loader):
    def _sdk_client_factory(client_type):
        # very simplified code
        api_key = load_api_key()
        if client_type == 'User':
            return some_sdk.user.Client(api_key)
        raise ValueError(f"unknown client type: {client_type}")
    return sdk_client_factory

def sdk_data_transfer(client_factory: sdk_client_factory, formatter: some_sdk.Formatter, context: object):
    def _sdk_data_transfer(payload: dict)
        # very simplified code
        client = client_factory(payload['type'])
        client.publish(formatter.format(payload['body']), handler=context.invoked_function_arn)
    return _sdk_data_transfer

# ...
```

Configure and run in `main.py` file:

```python
# main.py
import os
from . import ioc

init_error = None

try:
    container = ioc.build_container(
        ssm_param_api_key=os.environ.get("SSM_PARAM_API_KEY"),
        ddb_status_table=os.environ.get("DDB_STATUS_TABLE"),
        format_type=os.environ.get("FORMAT_TYPE", "YAML"),
    )
except Exception as ex:
    init_error = ex


def lambda_handler(event: dict, context: object):
    if init_error:
        raise init_error

    container.lambda_context(context)

    return container.event_handler(event)
```

In this example `container` would be compiled once per Lambda Function life cycle,
while `lambda_handler` processes incoming requests sequentially, until it dies after idle timeout.
