"""
:py:mod:`pymco.rpc`
-------------------
MCollective RPC calls support.
"""
import logging

from pymco.listener import MultiResponseListener

LOG = logging.getLogger(__name__)


class SimpleAction(object):
    """Single RPC call to MCollective

    :arg config: :py:class:`pymco.config.Config` instance.
    :arg msg: A dictionary like object, usually a
        :py:class:`pymco.message.Message` instance.
    :arg \*\*kwargs: extra keyword arguments. Set the collective here if you
        aren't targeting the main collective.
    """
    def __init__(self, config, msg, agent, logger=LOG, **kwargs):
        self.logger = logger
        self.logger.debug("init rpc.SimpleAction")
        self.config = config
        self.msg = msg
        self.agent = agent
        self._connector = None
        self.collective = (kwargs.get('collective', None) or
                           self.config['main_collective'])

    @property
    def connector(self):
        if not self._connector:
            self._connector = self.config.get_connector()
        return self._connector

    def get_target(self):
        """MCollective RPC call target.

        :return: middleware target for the request.
        """
        return self.connector.get_target(collective=self.collective,
                                         agent=self.agent)

    def get_reply_target(self):
        """MCollective RPC call reply target.

        This should build the subscription target required for listening replies
        to this RPC call.

        :return: middleware target for the response.
        """
        return self.connector.get_reply_target(collective=self.collective,
                                               agent=self.agent)

    def call(self, timeout=5):
        """Make the RPC call.

        It should subscribe to the reply target, execute the RPC call and wait
        for the result.

        :arg timeout: RPC call timeout.
        :return: a dictionary like object with response.
        :raise: :py:exc:`pymco.exc.TimeoutError` if expected messages don't
            arrive in ``timeout`` seconds.
        """
        self.logger.debug("connecting, wait=True")
        self.connector.connect(wait=True)
        reply_target = self.get_reply_target()
        self.logger.debug("subscribing to destination={r}".format(r=reply_target))
        self.connector.subscribe(destination=reply_target)
        self.logger.debug("sending")
        self.connector.send(self.msg,
                            self.get_target(),
                            **{'reply-to': reply_target})
        self.logger.debug("receiving replies, timeout={t}".format(t=timeout))
        result = self.connector.receive(timeout=timeout)
        self.logger.debug("disconnecting")
        self.connector.disconnect()
        return result


class CollectionAction(SimpleAction):
    """
    RPC call that expects multiple answers
    """
    def call(self, timeout=5):
        """Make the RPC call.

        It should subscribe to the reply target, execute the RPC call and wait
        for the results.

        :arg timeout: RPC call timeout.
        :return: a dictionary like object with response.
        :raise: :py:exc:`pymco.exc.TimeoutError` if expected messages don't
            arrive in ``timeout`` seconds.
        """
        self.logger.debug("connecting, wait=True")
        self.connector.connect(wait=True)
        reply_target = self.get_reply_target()
        self.logger.debug(
            "subscribing to destination={r}".format(r=reply_target)
        )
        self.connector.subscribe(destination=reply_target)
        self.logger.debug("sending")
        self.connector.send(
            self.msg, self.get_target(), **{'reply-to': reply_target}
        )
        self.logger.debug("receiving replies, timeout={t}".format(t=timeout))
        self.logger.debug(
            "setting up MultiResponseListener, timeout={t}".format(t=timeout)
        )
        response_listener = MultiResponseListener(
            timeout=timeout,
            security=self.config.get_security(), use_b64=self.connector.use_b64
        )
        self.connector.connection.set_listener(
            'response_listener', response_listener
        )
        self.logger.debug("listener waiting for message...")
        response_listener.wait_on_message()
        self.logger.debug("listener wait exited.")
        result = response_listener.responses
        self.logger.debug("disconnecting")
        self.connector.disconnect()
        return result
