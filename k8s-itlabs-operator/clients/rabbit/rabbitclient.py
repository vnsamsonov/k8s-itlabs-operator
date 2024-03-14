import base64
import logging
from abc import ABCMeta, abstractmethod

import requests
import ujson
from clients.rabbit.exceptions import RabbitClientError
from clients.rabbit.settings import RABBIT_TIMEOUT
from exceptions import InfrastructureServiceProblem
from utils.common import join

app_logger = logging.getLogger("rabbit_logger")


class AbstractRabbitClient:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_rabbit_user(self, user: str):
        raise NotImplementedError

    @abstractmethod
    def create_rabbit_user(self, user: str, password: str):
        raise NotImplementedError

    @abstractmethod
    def delete_rabbit_user(self, user: str):
        raise NotImplementedError

    @abstractmethod
    def get_rabbit_vhost(self, vhost: str):
        raise NotImplementedError

    @abstractmethod
    def create_rabbit_vhost(self, vhost: str):
        raise NotImplementedError

    @abstractmethod
    def delete_rabbit_vhost(self, vhost: str):
        raise NotImplementedError

    @abstractmethod
    def get_user_vhost_permissions(self, user, vhost):
        raise NotImplementedError

    @abstractmethod
    def create_user_vhost_permissions(self, user, vhost):
        raise NotImplementedError


class RabbitClient(AbstractRabbitClient):

    def __init__(self, url: str, user: str, password: str):
        self.url = url
        self.user = user
        self.password = password

    def get_rabbit_user(self, user: str):
        return self._send_rabbit_request(endpoint=f"/users/{user}")

    def create_rabbit_user(self, user: str, password: str):
        app_logger.info(
            "Creating user '%(user)s' in rabbit '%(url)s'"
            % {"user": user, "url": self.url}
        )
        data = {"password": password, "tags": ""}
        return self._send_rabbit_request(
            endpoint=f"/users/{user}", method="PUT", data=data
        )

    def delete_rabbit_user(self, user: str):
        app_logger.info(
            "Deleting user '%(user)s' in rabbit '%(url)s'"
            % {"user": user, "url": self.url}
        )
        self._send_rabbit_request(
            endpoint=f"/users/{user}", method="DELETE", data={}
        )

    def get_rabbit_vhost(self, vhost: str):
        return self._send_rabbit_request(endpoint=f"/vhosts/{vhost}")

    def create_rabbit_vhost(self, vhost: str):
        app_logger.info(
            "Creating vhost '%(host)s' in rabbit %(url)s"
            % {"host": vhost, "url": self.url}
        )
        return self._send_rabbit_request(
            endpoint=f"/vhosts/{vhost}", method="PUT", data={}
        )

    def delete_rabbit_vhost(self, vhost: str):
        app_logger.info(
            "Creating vhost '%(host)s' in rabbit %(url)s"
            % {"host": vhost, "url": self.url}
        )
        self._send_rabbit_request(
            endpoint=f"/vhosts/{vhost}", method="DELETE", data={}
        )

    def get_user_vhost_permissions(self, user, vhost):
        return self._send_rabbit_request(
            endpoint=f"/permissions/{vhost}/{user}"
        )

    def create_user_vhost_permissions(self, user, vhost):
        app_logger.info(
            "Configuring user '%(user)s' privileges to vhost '%(host)s' "
            "in rabbit '%(url)s'"
            % {"user": user, "host": vhost, "url": self.url}
        )
        data = {"configure": ".*", "write": ".*", "read": ".*"}
        return self._send_rabbit_request(
            endpoint=f"/permissions/{vhost}/{user}", method="PUT", data=data
        )

    def _send_rabbit_request(self, endpoint, data=None, method="GET"):
        endpoint = join(self.url, f"/api{endpoint}")

        encoded_user_pass = base64.b64encode(
            f"{self.user}:{self.password}".encode("UTF-8")
        ).decode("UTF-8")
        headers = {
            "Authorization": f"Basic {encoded_user_pass}",
            "content-type": "application/json",
        }
        try:
            response = requests.request(
                method=method,
                url=endpoint,
                data=ujson.dumps(data),
                headers=headers,
                timeout=RABBIT_TIMEOUT,
            )

            if response.ok:
                return response.json() if method == "GET" else None

            if response.status_code == 404:
                return None

            raise InfrastructureServiceProblem(
                "Rabbit", RabbitClientError(response)
            )
        except Exception as e:
            raise InfrastructureServiceProblem("Rabbit", e)
