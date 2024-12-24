from evopy.environment.base import BaseEnvironment
from evopy.interface.base import BaseInterface


class InterfaceEnvironment(BaseEnvironment):

    _active_interface: bool = True

    def __init__(self, options, **kwargs):
        self._components.append("interface")

        self._active_interface = self._active_interface and options.active_interface
        if self._active_interface:
            self.interface: BaseInterface = options.interface

        super().__init__(options, **kwargs)
