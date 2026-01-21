import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'superman.jpg'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_jpg = 'image/jpeg'
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    
    image_bytes = BytesIO(image_bytes)

    async with DialBucketClient(API_KEY, DIAL_URL) as bucket_client:
        result = await bucket_client.put_file(file_name, mime_type_jpg, image_bytes)
    
    return Attachment(title=file_name, url=result["url"], type=mime_type_jpg)

async def _put_image2() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_jpg = 'image/png'
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    
    image_bytes = BytesIO(image_bytes)

    async with DialBucketClient(API_KEY, DIAL_URL) as bucket_client:
        result = await bucket_client.put_file(file_name, mime_type_jpg, image_bytes)
    
    return Attachment(title=file_name, url=result["url"], type=mime_type_jpg)


async def start() -> None:
    attachment = await _put_image()
    attachment2 = await _put_image2()
    print(attachment)
    print(attachment2)
    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gemini-2.5-pro", API_KEY)
    result = client.get_completion(messages=[
        Message(role=Role.SYSTEM, content="You are detective and need to try your best to solve the case. You will be presented with the evidence and need to find the connection between them. You answer should be short and concise."),
        Message(role=Role.USER, content="What do you see on this picture?", custom_content=CustomContent(attachments=[attachment])),
        Message(role=Role.USER, content="How it corelates to the other picture?", custom_content=CustomContent(attachments=[attachment2]))
    ])
    print(result.content)
    # TODO:
    #  1. Create DialModelClient
    #  2. Upload image (use `_put_image` method )
    #  3. Print attachment to see result
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis


asyncio.run(start())
