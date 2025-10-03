import logging as lg


logg_levels_str: dict[str, int] = {
    "Debug": lg.DEBUG,
    "Info": lg.INFO,
    "Warning": lg.WARNING,
    "Error": lg.ERROR,
    "Critical": lg.CRITICAL
}

def create_logger(active_c_logg: bool, c_logg_level: str, c_logg_format: str, active_f_logg: bool, logg_file_name: str,
                  f_logg_level: str, f_logg_format: str, filtered_components: list[str]):
    """
    Create a logger with the specified settings
    """
    logger = lg.getLogger('evopy_logger')
    logger.setLevel(lg.DEBUG)

    if len(filtered_components):
        filter_comp = ComponentFilter(filtered_components)
        logger.addFilter(filter_comp)

    if active_c_logg:
        c_handler = lg.StreamHandler()
        c_handler.setLevel(logg_levels_str[c_logg_level])
        c_handler.setFormatter(lg.Formatter(c_logg_format))
        logger.addHandler(c_handler)

    if active_f_logg:
        f_handler = lg.FileHandler(logg_file_name, mode="w")
        f_handler.setLevel(logg_levels_str[f_logg_level])
        f_handler.setFormatter(lg.Formatter(f_logg_format))
        logger.addHandler(f_handler)

    return logger


class ComponentFilter(lg.Filter):

    def __init__(self, filtered_comp) -> None:
        super().__init__()
        self._filtered_comp: list[str] = filtered_comp

    def filter(self, record):
        component, *_ = record.msg.split(maxsplit=1)
        return component in self._filtered_comp
