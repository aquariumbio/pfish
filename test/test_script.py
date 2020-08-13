import pydent

aq = pydent.AqSession("neptune", "aquarium", "http://localhost:3000")


code_objects = {}

component_names = ['protocol', 'precondition', 'cost_model', 'documentation', 'test', 'source']

for name in component_names:
    code_objects[name] = aq.Code.new(name=name, content='')

# generate new name each time and then get entry once created 
ot = aq.OperationType.new(name="test creation 5555", category="testing", 
                            protocol=code_objects['protocol'],
                            precondition=code_objects['precondition'],
                            documentation=code_objects['documentation'],
                            cost_model=code_objects['cost_model'])
ot.field_types = []

aq.utils.create_operation_type(ot)

lib = aq.Library(name="test yet again", category="testing", source=code_objects['source'])

aq.utils.create_library(lib)
