import base64
from pathlib import Path

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task._models.conversation import Conversation
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl


def start() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "superman.jpg"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    base64_image_url = f"data:image/jpeg;base64,{base64_image}"


    client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gemini-2.5-pro", API_KEY)
    conv = Conversation()
    conv.add_message(ContentedMessage(role=Role.SYSTEM, content=[TxtContent(text="You are a sarcastic poet. You should always answer in haiku.")]))
    conv.add_message(ContentedMessage(role=Role.USER, content=[TxtContent(text="What do you see on this picture?")]))
    #conv.add_message(ContentedMessage(role=Role.USER, content=[ImgContent(image_url=ImgUrl(url="https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"))]))
    conv.add_message(ContentedMessage(role=Role.USER, content=[ImgContent(image_url=ImgUrl(url=base64_image_url))]))

    result = client.get_completion(conv.get_messages())
    print(result.content)


start()