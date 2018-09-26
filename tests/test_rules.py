from business_rules.engine import check_condition
from business_rules import export_rule_data
from business_rules import run_all
from business_rules.actions import rule_action, BaseActions
from business_rules.variables import BaseVariables, string_rule_variable, numeric_rule_variable, boolean_rule_variable
from business_rules.fields import FIELD_TEXT, FIELD_NUMERIC, FIELD_SELECT

from . import TestCase


class SomeVariables(BaseVariables):

    @string_rule_variable()
    def foo(self):
        return "foo"

    @numeric_rule_variable(label="Diez")
    def ten(self):
        return 10

    @numeric_rule_variable(label="num")
    def num(self):
        return 5

    @numeric_rule_variable(label="num_param", params={'number': FIELD_NUMERIC})
    def num_param(self, number):
        return number + 1

    @boolean_rule_variable()
    def true_bool(self):
        return True


class SomeActions(BaseActions):

    def __init__(self):
        self._baz = 'Not chosen'

    @rule_action(params={"foo": FIELD_NUMERIC})
    def some_action(self, foo): pass

    @rule_action(label="woohoo", params={"bar": FIELD_TEXT})
    def some_other_action(self, bar):
        return bar

    @rule_action(params=[{'fieldType': FIELD_SELECT,
                          'name': 'baz',
                          'label': 'Baz',
                          'options': [
                            {'label': 'Chose Me', 'name': 'chose_me'},
                            {'label': 'Or Me', 'name': 'or_me'}
                        ]}])
    def some_select_action(self, baz):
        self._baz = baz


class RulesTests(TestCase):
    """ Integration test, using the library like a user would.
    """
    def test_rules(self):

        rules = [
            {
            "conditions": {"all": [{
                    "name": "num_param",
                    "operator": "equal_to",
                    "params": {"number": 4},
                    "value": 5,
                },
                {
                    "name": "num",
                    "operator": "equal_to",
                    "value": 5,
                },
            ]},
            "actions": [{
                "name": "some_select_action",
                "params": {"baz": 'chose_me'},
            },],
                }
            ]

        actions = SomeActions()

        run_all(rule_list=rules,
                defined_variables=SomeVariables(),
                defined_actions=actions,
                stop_on_first_trigger=False
            )

        self.assertEqual(actions._baz, 'chose_me')
