""" 
Defines the Mixin class
"""


class Mixin:
    """
    Mixin class for components.
    The Mixin class is used to define the requirements and suggestions of a component.
    """

    _requirements: dict[list] = {}
    _suggests: dict[list] = {}
    _component_type: str = "None"

    @classmethod
    def set_component_type(cls, component_type: str):
        """
        Set the component type.
        The component type is used to identify the component.

        Args:
            component_type (str): Type of the component.
        """
        cls._component_type = component_type

    @classmethod
    def add_requirement(cls, name, component_class):
        """
        Add a requirement to the component.
        The requirements are necessary for the component to work.

        Args:
            name (str): Name of the requirement.
            component_class (type): Required component.
        """
        if component_class not in cls._requirements[name]:
            cls._requirements[name] = []
        cls._requirements[name].append(component_class)

    @classmethod
    def get_requirements(cls) -> dict:
        """
        Get the requirements of the component.
        The requirements are necessary for the component to work.

        Returns:
            dict: Requirements of the component.
        """
        return cls._requirements

    @classmethod
    def del_requirements(cls, component_name: str):
        """
        Delete a requirement from the component.
        The requirements are necessary for the component to work.

        Args:
            component_name (str): Name of the requirement.
        """
        del cls._requirements[component_name]

    @classmethod
    def add_suggest(cls, name, component_class):
        """
        Add a suggestion to the component.
        The suggestions are optional for the component to work.

        Args:
            name (str): Name of the suggestion.
            component_class (type): Suggested component.
        """
        if component_class not in cls._suggests[name]:
            cls._suggests[name] = []
        cls._suggests[name].append(component_class)

    @classmethod
    def get_suggests(cls) -> dict:
        """
        Get the suggestions of the component.
        The suggestions are optional for the component to work.

        Returns:
            dict: Suggestions of the component.
        """
        return cls._suggests

    @classmethod
    def del_suggests(cls, component_name: str):
        """
        Delete a suggestion from the component.
        The suggestions are optional for the component to work.

        Args:
            component_name (str): Name of the suggestion.
        """
        del cls._suggests[component_name]
