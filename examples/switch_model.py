"""The same client drives every hosted model listed in fish_audio_api.MODELS."""
from fish_audio_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"text": "Hello, this is a test of MiMo speech synthesis."}, model="xiaomi/mimo-tts")
print(output)
