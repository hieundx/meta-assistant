from openai import OpenAI

from meta_assistant import logger

class TextGenerator:
    @staticmethod
    def generate(key: str, model: str, input: str, instruction: str):
        client = OpenAI(api_key=key)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input,
                }
            ],
            model="gpt-3.5-turbo",
        )

        return chat_completion.choices[0].message.content
