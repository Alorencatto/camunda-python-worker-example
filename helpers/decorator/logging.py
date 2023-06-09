from datetime import datetime,timezone
from ..camunda.worker import ExternalTaskException


def logger(fn):
    """
    Logger decorator
    :param fn:
    :return:
    """
    def inner(*args,**kwargs):

        called_at : datetime = datetime.now(timezone.utc)
        to_execute = fn(*args, **kwargs)

        print(fn.__dict__)

        # TODO : Implement Insert on MongoDB
        print('{0} executed. Logged at {1}'.format(fn.__name__, called_at))
        return to_execute

    return inner

def task(fn):
    """
    Decorator para tratamento de Exception no Camunda
    :param fn:
    :return:
    """

    def inner(*args, **kwargs):

        try:
            called_at: datetime = datetime.now(timezone.utc)
            to_execute = fn(*args, **kwargs)

            # print(*kwargs.items())

            # TODO : Implement Insert on MongoDB
            print('{0} executed. Logged at {1}'.format(fn.__name__, called_at))
            return to_execute
        except Exception as e:
            raise ExternalTaskException(message=str(e))

    return inner

def apiTransaction(fn):

    def inner(*args, **kwargs):
        try:
            to_execute = fn(*args, **kwargs)
        except AttributeError:
            print("Nothing to return...")

    return inner()

