import inspect
import string
from collections import OrderedDict

from typing import *

from behave import matchers, model as behave_model
from goat import model
from goat.types import TYPE_TO_PARSE_TYPE_MAP


class GoatFormatter(string.Formatter):
    pass


class GoatMatcher(matchers.CFParseMatcher):
    def __init__(self, func, pattern, step_type=None):
        func, pattern = self.convert(func, pattern)
        super().__init__(func, pattern, step_type)

    def match(self, step) -> behave_model.Match:
        result = self.check_match(step)
        if result is None:
            return None
        return model.Match(self.func, result)

    def check_match(self, step) -> List[behave_model.Argument]:
        """Also add the implicit parameters from the context"""
        # TODO implement context handling
        return super().check_match(step)

    def convert_type_to_parse_type(self, parameter):
        annotation = parameter.annotation
        if not isinstance(annotation, str):
            annotation = annotation.__name__
        annotation = TYPE_TO_PARSE_TYPE_MAP.get(annotation, annotation)
        return annotation

    def convert(self, func: Callable, pattern: str) -> Tuple[Callable, str]:
        """Convert the goat step string to CFParse String"""
        # TODO check if the return of the function is really needed
        signature = inspect.signature(func)
        parameters = OrderedDict()
        for parameter in signature.parameters.values():
            annotation = self.convert_type_to_parse_type(parameter)
            parameters[parameter.name] = "{%s:%s}" % (parameter.name, annotation)

        try:
            # handle indexed parameters like {} and {0}
            return func, GoatFormatter().format(pattern, *parameters.values())
        except KeyError:
            # handle name parameters like {name}
            return func, GoatFormatter().format(pattern, **parameters)