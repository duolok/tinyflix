import aws_cdk as core
import aws_cdk.assertions as assertions

from tinyflix_back.tinyflix_back_stack import TinyflixBackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in tinyflix_back/tinyflix_back_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TinyflixBackStack(app, "tinyflix-back")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
