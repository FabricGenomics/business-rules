import inspect
from functools import wraps
from . import fields
from .utils import fn_name_to_pretty_label
from .operators import (BaseType,
                        NumericType,
                        StringType,
                        BooleanType,
                        SelectType,
                        SelectMultipleType)

class BaseVariables(object):
    """ Classes that hold a collection of variables to use with the rules
    engine should inherit from this.
    """
    @classmethod
    def get_all_variables(cls):
        methods = inspect.getmembers(cls)
        return [{'name': m[0],
                 'label': m[1].label,
                 'field_type': m[1].field_type.name,
                 'options': m[1].options,
                 'params': m[1].params,
                } for m in methods if getattr(m[1], 'is_rule_variable', False)]

def _validate_action_parameters(func, params):
    """ Verifies that the parameters specified are actual parameters for the
    function `func`, and that the field types are FIELD_* types in fields.
    """
    if params is not None:
        # Verify field name is valid
        valid_fields = [getattr(fields, f) for f in dir(fields) \
                if f.startswith("FIELD_")]
        for param in params:
            param_name, field_type = param['name'], param['fieldType']
            if param_name not in func.__code__.co_varnames:
                raise AssertionError("Unknown parameter name {0} specified for"\
                        " action {1}".format(
                        param_name, func.__name__))

            if field_type not in valid_fields:
                raise AssertionError("Unknown field type {0} specified for"\
                        " action {1} param {2}".format(
                        field_type, func.__name__, param_name))

def rule_variable(field_type, label=None, options=None, params=None):
    """ Decorator to make a function into a rule variable
    """
    options = options or []
    def wrapper(func):
        if not (type(field_type) == type and issubclass(field_type, BaseType)):
            raise AssertionError("{0} is not instance of BaseType in"\
                    " rule_variable field_type".format(field_type))
        func.field_type = field_type
        params_ = params
        if isinstance(params, dict):
            params_ = [dict(label=fn_name_to_pretty_label(name),
                           name=name,
                           fieldType=param_field_type) \
                      for name, param_field_type in params.items()]
        _validate_action_parameters(func, params_)
        func.is_rule_variable = True
        func.label = label \
                or fn_name_to_pretty_label(func.__name__)
        func.options = options
        func.params = params_
        return func
    return wrapper


def _rule_variable_wrapper(field_type, label, params):
    if callable(label):
        # Decorator is being called with no args, label is actually the decorated func
        return rule_variable(field_type)(label)
    return rule_variable(field_type, label=label, params=params)

def numeric_rule_variable(label=None, params=None):
    return _rule_variable_wrapper(NumericType, label, params)

def string_rule_variable(label=None, params=None):
    return _rule_variable_wrapper(StringType, label, params)

def boolean_rule_variable(label=None, params=None):
    return _rule_variable_wrapper(BooleanType, label, params)

def select_rule_variable(label=None, options=None, params=None):
    return rule_variable(SelectType, label=label, options=options, params=params)

def select_multiple_rule_variable(label=None, options=None, params=None):
    return rule_variable(SelectMultipleType, label=label, options=options, params=params)
