from __future__ import absolute_import, unicode_literals

from draftjs_exporter.entities.null import Null
from draftjs_exporter.error import ExporterException


class EntityException(ExporterException):
    pass


class EntityState():
    def __init__(self, root_element, entity_decorators, entity_map):
        self.entity_decorators = entity_decorators
        self.entity_map = entity_map
        self.entity_stack = [(Null().call(root_element, {}), {})]

    def apply(self, command):
        if (command.name == 'start_entity'):
            self.start_command(command)
        elif (command.name == 'stop_entity'):
            self.stop_command(command)

    def current_parent(self):
        return self.entity_stack[-1][0]

    def get_entity_details(self, command):
        key = str(command.data)
        details = self.entity_map.get(key)

        if details is None:
            raise EntityException('Entity "%s" does not exist in the entityMap' % key)

        return details

    def get_entity_decorator(self, entity_details):
        type = entity_details.get('type')
        decorator = self.entity_decorators.get(type)

        if decorator is None:
            raise EntityException('Decorator "%s" does not exist in entity_decorators' % type)

        return decorator

    def start_command(self, command):
        entity_details = self.get_entity_details(command)
        decorator = self.get_entity_decorator(entity_details)

        new_element = decorator.call(self.current_parent(), entity_details)

        self.entity_stack.append([new_element, entity_details])

    def stop_command(self, command):
        entity_details = self.get_entity_details(command)
        expected_entity_details = self.entity_stack[-1][1]

        if expected_entity_details != entity_details:
            raise EntityException('Expected {0}, got {1}'.format(expected_entity_details, entity_details))

        self.entity_stack.pop()