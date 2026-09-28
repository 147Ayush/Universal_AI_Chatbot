# Temporary helper: prints the model IDs your Groq key can actually use.
from groq import Groq
from app.config.settings import get_settings

client = Groq(api_key=get_settings().groq_api_key)

for model in client.models.list().data:
    print(model.id)