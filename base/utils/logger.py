import logging as lg

# Log Settings
c_logg_level: int = lg.WARNING
c_logg_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logg_file_name: str = "evo.log"
f_logg_level: int = lg.INFO
f_logg_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logg_levels_str: dict = {"debug": lg.DEBUG, "info": lg.INFO, "warning": lg.WARNING, "error": lg.ERROR, "critical": lg.CRITICAL}
filtered_components: list[str] = []



def create_logger():
    """
    Create a logger with the specified settings
    """
    logger = lg.getLogger('my_app_logger')
    logger.setLevel(lg.DEBUG)

    if len(filtered_components):
        filter = ComponentFilter(filtered_components)
        logger.addFilter(filter)

    # Create handlers
    c_handler = lg.StreamHandler()
    f_handler = lg.FileHandler(logg_file_name, mode="w")
    c_handler.setLevel(c_logg_level)
    f_handler.setLevel(f_logg_level)

    # Create formatters and add them to handlers
    c_handler.setFormatter(lg.Formatter(c_logg_format))
    f_handler.setFormatter(lg.Formatter(f_logg_format))

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


class ComponentFilter(lg.Filter):

    def __init__(self, filtered_comp) -> None:
        super().__init__()
        self._filtered_comp: list[str] = filtered_comp

    def filter(self, record):
        component, *_ = record.msg.split(maxsplit=1)
        return component in self._filtered_comp
