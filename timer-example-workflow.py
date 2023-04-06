# -*- coding: utf-8 -*-

from camunda.helpers.camunda import worker


def test() -> dict:

    print("Aqui")

    return {}

if __name__ == '__main__':
    url = 'http://postgresql-dev.intradesk:8080/engine-rest'
    worker_id = '1'

    # Call instance start
    # start_instance()

    # Create worker instance
    worker = worker.Worker(url=url, worker_id=worker_id)

    worker.subscribe(
        topic='task1',
        func=test
    )

    worker.run()
