# -*- coding: utf-8 -*-
import os
import random
import sys
import typing
from datetime import datetime
from dotenv import load_dotenv

import pycamunda.variable

from camunda.helpers.camunda import worker
from camunda.helpers.camunda.worker import ExternalTaskException

import pycamunda.processdef
import pycamunda.processinst
import pycamunda.task
from helpers.database.mongodb import Database
from helpers.decorator.logging import logger, apiTransaction,task
from helpers.api.generic import APIRequest

# TODO : Container on docker

load_dotenv()


def handleError() -> None:
    print("handle error...")


def handleRequestValidation(v_url: pycamunda.variable.Variable,v_status_code: pycamunda.variable.Variable) -> dict:
    print("Validating...")

    if 'io' in v_url.value:
        raise ExternalTaskException(message="Invalid url")

    return {}

@task
def handleBException(responseStatusCode: pycamunda.variable.Variable) -> dict:
    print(f"Handling buissness exception ({responseStatusCode.value})...")

    return {}


@task
def handleFinalProcess(responseStatusCode: pycamunda.variable.Variable) -> dict:

    print(f"Status code : {responseStatusCode.value}")

    Database.initialize()
    Database.insert("camunda_dev", {"responseStatusCode": responseStatusCode.value})

    return {}


if __name__ == '__main__':
    camunda_base_url: str = os.environ.get("CAMUNDA_HOST")
    worker_id = '1'

    # Create worker instance
    worker = worker.Worker(url=camunda_base_url, worker_id=worker_id)

    worker.subscribe(
        topic='dev-api-consume-validate-request',
        func=handleRequestValidation,
        variables=["v_url","v_status_code"]
    )

    worker.subscribe(
        topic='dev-api-consume-handle-b-exception',
        func=handleBException,
        variables=["responseStatusCode"]
    )

    worker.subscribe(
        topic='dev-api-consume-final-process',
        func=handleFinalProcess,
        variables=["responseStatusCode"]
    )

    worker.run()
