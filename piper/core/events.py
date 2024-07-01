#  Copyright (c) Christian Corsica. All Rights Reserved.


class _Dispatcher(object):
    # used to keep track of Manager in order to make it a singleton.
    instance = None

    def __init__(self, *args, **kwargs):
        """
        Handles event callbacks throughout piper functions.
        """
        super(_Dispatcher, self).__init__(*args, **kwargs)
        self.events = {}

    def listen(self, event_name, method):
        """
        Makes the given method a callback method since it will be called everytime the given event_name is updated.
        As long as the responsible party adds the call method correctly.

        NOTE: Listener must remove/pop listen method on unregister by using manager.unlisten()!

        Args:
            event_name (string): Event name that will be called.

            method (Callable): Function that will be called when event_name is called.
        """
        listeners = self.events.setdefault(event_name, [])
        listeners.append(method)

    def unlisten(self, event_name, method):
        """
        Removes the given method from listening for the given event_name.

        Args:
            event_name (string): Name of event that would call given method.

            method (Callable): Function to remove from listening of given event_name.
        """
        self.events[event_name].remove(method)

    def call(self, event_name):
        """
        Calls all the listeners of the given event_name.

        Args:
            event_name (string): Name of event that holds listeners.
        """
        listeners = self.events.setdefault(event_name, [])
        [callback() for callback in listeners]


def getDispatcher():
    """
    Used to create or get the Piper event dispatcher, there can only be ONE in the scene at a time.

    Returns:
        (_Dispatcher): Piper event dispatcher.
    """
    _Dispatcher.instance = _Dispatcher() if _Dispatcher.instance is None else _Dispatcher.instance
    return _Dispatcher.instance


dispatcher = getDispatcher()
