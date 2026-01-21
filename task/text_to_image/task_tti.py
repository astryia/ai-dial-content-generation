import asyncio
from datetime import datetime
from pathlib import Path

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    async with DialBucketClient(API_KEY, DIAL_URL) as bucket_client:
        project_root = Path(__file__).parent.parent.parent
        # all attachments with url
        for attachment in [a for a in attachments if a.url]:
            content = await bucket_client.get_file(attachment.url)
            ext = attachment.url.split(".")[-1]
            image_path = project_root / f"generated_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            with open(image_path, "wb") as fout:
                fout.write(content)
            print(f"{attachment.title} saved to {image_path}")

async def start() -> None:
    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "dall-e-3", API_KEY)
    result = client.get_completion(messages=[
        Message(role=Role.SYSTEM, content="You are cartoon artist. You task is to generate single representation of cartoon character by user description. Charter should not be realistic, but cartoonish. Charecter should be completely drawn in one frame, fused together from multiple parts. No background, no text, no other elements."),
        Message(role=Role.USER, content="Chimpanzini Bananini")
    ], custom_fields={"style": "vivid"})
    attachments = result.custom_content.attachments
    await _save_images(attachments)
    # TODO:
    #  1. Create DialModelClient
    #  2. Generate image for "Sunny day on Bali"
    #  3. Get attachments from response and save generated message (use method `_save_images`)
    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)


asyncio.run(start())
