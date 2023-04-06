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
from helpers.decorator.logging import logger,apiTransaction
from helpers.api.generic import APIRequest

# TODO : Default error handler
# TODO : Forçar raise de error para entender o comportamento
# TODO : Container on docker

load_dotenv()


@logger
def generate_random_number(
        range_min: pycamunda.variable.Variable, range_max: pycamunda.variable.Variable
) -> typing.Dict[str, int]:
    """
    TODO
    :param range_min:
    :param range_max:
    :return:
    """
    try:
        number = random.randrange(range_min.value, range_max.value)
    except ValueError:
        raise worker.ExternalTaskException(message='invalid input')

    return {'number': number}


@logger
def print_number_greater_than_2(number: pycamunda.variable.Variable) -> typing.Dict:
    """
    TODO
    :param number:
    :return:
    """
    try:
        Database.initialize()

        Database.insert("camunda_dev", {"file": str(__file__), "number": number.value, "updated_at": datetime.now()})

    except Exception:
        raise ExternalTaskException(message='invalid input')

    return {}


@logger
def print_number(number: pycamunda.variable.Variable) -> typing.Dict:
    """
    TODO
    :param number:
    :return:
    """
    try:
        Database.initialize()

        Database.insert("camunda_dev", {"number": number.value})

    except Exception:
        raise ExternalTaskException(message='invalid input')

    return {}


@logger
@apiTransaction
def test_task(range_min: pycamunda.variable.Variable, range_max: pycamunda.variable.Variable) -> dict:
    """"""
    print("Starting testTask...")

    # r = Database.find("camunda_dev", {})
    # print(r)

    api_request : APIRequest = APIRequest(base_url="https://jsonplaceholder.typicode.comm")
    r = api_request(method="GET", route="/posts")

    print(r.json())

    return {}


@logger
def test_end_process(number: pycamunda.variable.Variable) -> dict:
    """"""
    return {}


def start_instance(url: str) -> None:
    start_instance = pycamunda.processdef.StartInstance(url=url, key='Process_0l0vhr7')
    start_instance.add_variable(name='range_min', value=0)
    start_instance.add_variable(name='range_max', value=10)
    process_instance = start_instance()


if __name__ == '__main__':
    # Call instance start
    # start_instance()

    camunda_base_url: str = os.environ.get("CAMUNDA_HOST")
    worker_id = '1'
    #
    # api_request: APIRequest = APIRequest(base_url="https://jsonplaceholder.typicode.comm")
    # r = api_request(method="GET", route="/posts")
    #
    # print(r.json())
    #
    # sys.exit(0)

    # Create worker instance
    worker = worker.Worker(url=camunda_base_url, worker_id=worker_id)

    worker.subscribe(
        topic='testtopic',
        func=test_task,
        variables=['range_min', 'range_max']
    )

    # worker.subscribe(
    #     topic='testtask1',
    #     func=generate_random_number,
    #     variables=['range_min', 'range_max']
    # )
    #
    # worker.subscribe(
    #     topic='testtaskreceive1',
    #     func=print_number_greater_than_2,
    #     variables=['number']
    # )
    #
    # worker.subscribe(
    #     topic='testtaskreceive2',
    #     func=print_number,
    #     variables=['number']
    # )
    #
    # worker.subscribe(
    #     topic='testendprocess',
    #     func=test_end_process,
    #     variables=['number']
    # )

    worker.run()
