from typing import Optional, Text

from linebot import WebhookHandler
from linebot.models.events import MessageEvent
from linebot.utils import LOGGER
from linebot.models.events import Event
from linebot.models.messages import Message
from pyassorted.asyncio.executor import run_func


def get_handler_key(event: "Event", message: Optional["Message"] = None) -> Text:
    """Get handler key.

    Parameters
    ----------
    event : Event
        The Line event.
    message : Optional[&quot;Message&quot;], optional
        The Line message, by default None

    Returns
    -------
    Text
        The handler key.
    """

    if message is None:
        return event.__name__
    else:
        return event.__name__ + "_" + message.__name__


class AsyncWebhookHandler(WebhookHandler):
    """Asynchronized Line bot webhook handler."""

    async def async_handle(self, body: Text, signature: Text) -> None:
        """Handle webhook.

        Parameters
        ----------
        body : str
            Webhook request body (as text)
        signature : str
            X-Line-Signature value (as text)
        """

        payload = self.parser.parse(body, signature, as_payload=True)

        for event in payload.events:
            func = None
            key = None

            if isinstance(event, MessageEvent):
                key = get_handler_key(event.__class__, event.message.__class__)
                func = self._handlers.get(key, None)

            if func is None:
                key = get_handler_key(event.__class__)
                func = self._handlers.get(key, None)

            if func is None:
                func = self._default

            if func is None:
                LOGGER.info("No handler of " + key + " and no default handler")
            else:
                await self.__async_invoke_func(func, event, payload)

    @classmethod
    async def __async_invoke_func(cls, func, event, payload) -> None:
        """Invoke function.

        Parameters
        ----------
        func : Callable
            Function to be invoked.
        event : Event
            The Line event.
        payload : Dict
            The Line payload.
        """

        (has_varargs, args_count) = cls.__get_args_count(func)
        if has_varargs or args_count == 2:
            await run_func(func, event, payload.destination)
        elif args_count == 1:
            await run_func(func, event)
        else:
            await run_func(func)
