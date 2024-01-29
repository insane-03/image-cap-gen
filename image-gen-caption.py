import requests
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

from openai import OpenAI

PAT = '627a72de170b44c6858405eae4f2e53d'
USER_ID = 'salesforce'
APP_ID = 'blip'
MODEL_ID = 'general-english-image-caption-blip'
MODEL_VERSION_ID = 'cdb690f13e62470ea6723642044f95e4'

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)
def get_desc(image_url):

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            url=image_url
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    print("Predicted concepts:")
    for concept in output.data.concepts:
        print("%s %.2f" % (concept.name, concept.value))

    # Uncomment this line to print the full Response JSON
    print(output)
    return output.data.text.raw

def gen_cap(image_description):

    # OpenAI API Key
    api_key = "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"
    client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
)

    try:
        response = client.chat.completions.create(
        messages=[
                {"role": "user", "content": f"Create a caption for the following image description: {image_description}"}
            ],
    model="gpt-3.5-turbo-16k",
)
        return response['choices'][0]['message']
    except Exception as e:
        return str(e)


# Example Usage
image_url = "https://images.unsplash.com/photo-1706396924378-e3d45b4f6d00?q=80&w=1964&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
desc = get_desc(image_url)
cap = gen_cap(desc)
print(cap)