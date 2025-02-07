"""
Defines the InterfaceEnvironment class.
It is a subclass of BaseEnvironment and is used to add interface capabilities to the environment.
"""

from evopy.environment.base import BaseEnvironment
from evopy.interface import BaseInterface


class InterfaceEnvironment(BaseEnvironment):
    """
    This is the InterfaceEnvironment class, a subclass of BaseEnvironment.
    It is used to add interface capabilities to the environment.

    Parameters:
        * interface (BaseInterface): the interface class to use
        * active_interface (bool): whether this interface is active or not
    """

    _active_interface: bool = True

    def __init__(self, options, **kwargs):
        self._components.append("interface")
        self._activations["interface"] = True and options.active_interface

        if self.is_active("interface"):
            self.interface: BaseInterface = options.interface

        super().__init__(options, **kwargs)

    def init_evolution(self):
        super().init_evolution()
        if self.is_active("interface"):
            self.interface.init_evolution()

    def end_evolution(self):
        super().end_evolution()
        if self.is_active("interface"):
            self.interface.end_evolution()

    def update_interface(self):
        """
        Updates the interface component.
        """
        if self.is_active("interface"):
            self.log("info", "Interface is updating")
            self.interface.update()

    def _new_generation(self):
        super()._new_generation()
        self.update_interface()
