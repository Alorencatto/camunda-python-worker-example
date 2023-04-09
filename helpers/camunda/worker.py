# -*- coding: utf-8 -*-

import typing

import pycamunda.externaltask
import pycamunda.variable


class ExternalTaskException(Exception):
    def __init__(
            self, *args, message: str, details: str = '', retry_timeout: int = 10000, **kwargs
    ):
        """Exception genérica para exceções nas tarefas externas.
        :param message: Mensagem de erro que descreve a razão da falha
        :param details: Detalhes do erro.
        :param retry_timeout: Timeout (milissegundos) até a tarefas se tornar disponível novamente.
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.details = details
        self.retry_timeout = retry_timeout


class Worker:

    def __init__(
            self,
            url: str,
            worker_id: str,
            max_tasks: int = 4,
            async_response_timeout: int = 5000
    ):
        """Worker que interage e completa tarefas externas no Camunda .
        :param url: REST API URL da engine.
        :param worker_id: Identificador do worker. Ex : 'microservice-python-ticket'.
        :param max_tasks: Número máximo de tarefas que o worker pode assumir simultâneamente.
        :param async_response_timeout: Tempo de intervalo na consulta na engine do Camunda (milissegundos).
        """
        self.fetch_and_lock = pycamunda.externaltask.FetchAndLock(
            url, worker_id, max_tasks, async_response_timeout=async_response_timeout
        )
        self.complete_task = pycamunda.externaltask.Complete(
            url, id_=None, worker_id=worker_id
        )
        self.handle_failure = pycamunda.externaltask.HandleFailure(
            url,
            id_='1',
            worker_id=worker_id,
            error_message='',
            error_details='',
            retries=0,
            retry_timeout=0,
        )

        self.stopped = False
        self.topic_funcs = {}

    def subscribe(
            self,
            topic: str,
            func: typing.Callable,
            lock_duration: int = 10000,
            variables: typing.Iterable[str] = None
    ):
        """Inscreve o worker em um tópico específico no workflow.
        :param topic: Tópico a se fazer a inscrição.
        :param func: Função Python que será executada ao receber o evento.
        :param lock_duration: Duração em milissegundos que as tarefas serão bloqueadas dentro do worker.
        :param variables: Variávis que serão passadas para a função referente ao processo.

        """
        self.fetch_and_lock.add_topic(topic, lock_duration, variables, False)
        self.topic_funcs[topic] = func

    def unsubscribe(self, topic):
        """Unsubscribe the worker from a topic.
        :param topic: The topic to unsubscribe from.
        """
        for i, topic_ in enumerate(self.fetch_and_lock.topics):
            if topic_['topicName'] == topic:
                del self.fetch_and_lock.topics[i]
                break

    def run(self):
        """Roda o worker."""
        while not self.stopped:
            tasks = self.fetch_and_lock()

            for task in tasks:
                try:
                    return_variables = self.topic_funcs[task.topic_name](**task.variables)
                except ExternalTaskException as exc:
                    print(f"Handling error here {exc.message}")
                    self.handle_failure.id_ = task.id_
                    self.handle_failure.error_message = exc.message
                    self.handle_failure.error_details = exc.details
                    self.handle_failure.retry_timeout = exc.retry_timeout

                    if task.retries is None:
                        self.handle_failure.retries = 1
                    else:
                        self.handle_failure.retries = task.retries - 1

                    self.handle_failure(
                        error_message=exc.message,
                        error_details=exc.details
                    )
                else:
                    self.complete_task.variables = {}
                    self.complete_task.id_ = task.id_
                    for variable, value in return_variables.items():
                        self.complete_task.add_variable(name=variable, value=value)
                    self.complete_task()
