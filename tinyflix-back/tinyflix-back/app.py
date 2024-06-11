import os
import aws_cdk as cdk

from tinyflix_back.tinyflix_back_stack import TinyflixBackStack

app = cdk.App()
TinyflixBackStack(app, "TinyflixBackStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()

