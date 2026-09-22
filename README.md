# Fish Audio API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/fish-audio/voice-changer?utm_source=github&utm_medium=ugc&utm_campaign=fish-audio-dev&utm_content=readme-badge&utm_term=tier-c)

Fish Audio is a voice platform built around voice cloning: text-to-speech in a cloned voice, and a speech-to-speech voice changer that keeps the words, timing and delivery of a source recording while replacing the voice. This repository is a small Python client for the Fish Audio API as hosted on Synexa, so you can convert a recording into another voice from a script with one `pip install` and an API token, without running the model yourself.

You get a blocking `run()` that uploads your two audio files and returns the converted clip, a non-blocking create-and-poll path for longer batches, and webhook delivery for pipelines that would rather not hold a connection open. The client has a single runtime dependency and no model weights, so it fits in a CLI tool, a Celery worker or a notebook. It is aimed at developers building dubbing, localisation, podcast post-production or game dialogue pipelines who want the Fish Audio voice changer as an HTTP call rather than a GPU deployment.

> **Try it now:** [https://synexa.ai/explore/fish-audio/voice-changer](https://synexa.ai/explore/fish-audio/voice-changer?utm_source=github&utm_medium=ugc&utm_campaign=fish-audio-dev&utm_content=readme-top&utm_term=tier-c) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About Fish Audio](#about-fish-audio)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No GPU to provision.** Speech-to-speech conversion with voice cloning needs a CUDA GPU with several gigabytes of VRAM plus the audio codec stack; the hosted endpoint runs on Synexa's fleet and you pay per conversion.
- **No environment to maintain.** Fish Audio's inference stack pulls in PyTorch, a vocoder and audio-processing libraries with tight version pins. The hosted endpoint removes that from your build.
- **No cold start on your side.** The model is already resident on the endpoint. You send two files and receive a converted file; there is no checkpoint to load into memory before the first request.
- **Predictable cost.** `fish-audio/voice-changer` is billed at $1.00 per run, and the companion `xiaomi/mimo-tts` text-to-speech model at $0.02 per run, so the cost of a batch is known before you submit it.

## Installation

```bash
pip install git+https://github.com/fish-audio-dev/fish-audio-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=fish-audio-dev&utm_content=readme-apikey&utm_term=tier-c)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import fish_audio_api

output = fish_audio_api.run({
    "audio": "https://example.com/input.png",
    "reference_audio": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from fish_audio_api import Client

client = Client(api_key="sk-...")
output = client.run({"audio": "https://example.com/input.png", "reference_audio": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`fish-audio/voice-changer`](https://synexa.ai/explore/fish-audio/voice-changer?utm_source=github&utm_medium=ugc&utm_campaign=fish-audio-dev&utm_content=readme-models&utm_term=tier-c) | audio-to-audio | Fish Audio speech-to-speech voice changer. Keeps the words, timing and delivery of your source recording but speaks them in a voice cloned from a second audio clip. | $1.0 |
| [`xiaomi/mimo-tts`](https://synexa.ai/explore/xiaomi/mimo-tts?utm_source=github&utm_medium=ugc&utm_campaign=fish-audio-dev&utm_content=readme-models&utm_term=tier-c) | text-to-audio | Xiaomi MiMo V2.5 text-to-speech. Speaks text with one of 9 built-in voices, clones a voice from a reference clip, or invents a new voice from a written description. | $0.02 |

The default model is **`fish-audio/voice-changer`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `fish-audio/voice-changer`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `audio` | file | yes | — | — | Source speech to convert (.mp3/.wav/.flac/.m4a/.ogg/.opus/.aac/.webm/.mp4). Its words, timing and delivery are kept; only the voice is replaced |
| `reference_audio` | file | yes | — | — | Audio of the target voice (.mp3/.wav/.flac/.m4a/.ogg/.opus/.aac/.webm/.mp4). It is cloned, used for the conversion, then discarded. 30 seconds or more of clean single-speaker speech works best |

### `xiaomi/mimo-tts`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `text` | string | yes | `Hello, this is a test of MiMo speech syn…` | — | Text to speak. A style tag may lead the text, e.g. '(happy)Hello there'; inline tags such as '(sigh)' are also supported. Tags are never spoken out loud. |
| `voice` | string | no | `Dean` | mimo_default, 冰糖, 茉莉, 苏打, 白桦, Mia, Chloe, Milo, Dean | Built-in voice. Mutually exclusive with reference and description |
| `reference` | file | no | — | — | A .wav/.mp3 clip whose voice gets cloned (Optional). 10-30 seconds of clean speech works best. Mutually exclusive with voice and description |
| `description` | string | no | — | — | A sentence that invents a new voice, e.g. 'man in his forties, deep and raspy, speaks slowly' (Optional). Every call invents a slightly different voice. Mutually exclusive with voice and reference |
| `instructions` | string | no | — | — | Plain-language style note, e.g. 'slow down, sound tired' (Optional). Never spoken out loud. Not allowed together with description, which already carries the style |
| `audio_format` | string | no | `wav` | wav, mp3 | Output audio format |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from fish_audio_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About Fish Audio

Fish Audio ([fish.audio](https://fish.audio)) is a voice platform developed by the Fish Audio team, who also maintain the open-source Fish Speech text-to-speech project on GitHub. The product covers text-to-speech with a large library of community voices, zero-shot voice cloning from a short reference clip, and a speech-to-speech voice changer. Fish Audio's models are known for handling multilingual input and for reproducing timbre from short reference clips without per-voice fine-tuning.

The voice changer is the capability this client wraps. Given a source recording and a reference clip of the target voice, the model keeps the source's content, timing, prosody and emphasis and re-renders it in the reference speaker's timbre. Typical outputs are a single audio file in the same length as the source. Quality depends heavily on the reference: thirty seconds or more of clean, single-speaker speech with no music or background noise gives the most faithful clone, and the reference voice is used only for that conversion and then discarded.

In practice the model is used for dubbing an actor's line into another character's voice, replacing a scratch narration with a licensed voice, anonymising a speaker while keeping their delivery, and producing consistent character dialogue for games from a single voice actor.

The hosted endpoint used by this client is `fish-audio/voice-changer` on Synexa, which is Fish Audio's own voice changer model served through Synexa's API. The client also exposes `xiaomi/mimo-tts`, a text-to-speech model from Xiaomi that can speak with one of nine built-in voices, clone a voice from a reference clip or invent one from a written description; it is a different model, included because voice conversion and speech synthesis are usually needed together. Fish Audio's own platform, pricing and open-source releases are at [fish.audio](https://fish.audio).

**Official project:** https://fish.audio

## Use cases

- **Dub a line into another character's voice** — pass the actor's take as `audio` and a clip of the target character as `reference_audio`; the timing stays aligned to the original video.
- **Replace a scratch narration** — record the voiceover yourself, then convert it to the final licensed voice with a single `run()` call instead of re-recording.
- **Anonymise a speaker** — convert interview or support-call audio into a neutral reference voice while preserving what was said and how it was said.
- **Consistent game dialogue** — have one voice actor record every character, then batch-convert each line to its character's reference clip through the poll-based path.
- **Localisation QA** — after generating a translated voiceover with `xiaomi/mimo-tts`, convert it to the original presenter's voice so the localised version sounds like the same person.
- **Podcast repair** — re-render a segment that was recorded on a bad microphone by converting a clean re-read back into the host's voice from the good takes.

## FAQ

**Is there a Fish Audio API?**

Yes. Fish Audio offers an API on its own platform, and the voice changer model is also hosted on Synexa as `fish-audio/voice-changer`. This client talks to the Synexa endpoint, which accepts a source audio file and a reference clip and returns the converted audio.

**How much does the Fish Audio API cost through this client?**

The hosted `fish-audio/voice-changer` endpoint is billed at $1.00 per run. The companion `xiaomi/mimo-tts` text-to-speech model is $0.02 per run. There is no subscription or minimum; you are charged per completed conversion.

**Can I run Fish Audio without a GPU?**

With this client, yes. The model runs on Synexa's GPUs; your machine only needs Python and network access. Running Fish Audio's models locally requires a CUDA GPU.

**Does this client work with the open-source Fish Speech repo?**

No. It does not load local weights or talk to a self-hosted Fish Speech server; it only calls the hosted endpoint. If you self-host Fish Speech, use that project's own API.

**What input formats does it accept?**

Both `audio` and `reference_audio` accept .mp3, .wav, .flac, .m4a, .ogg, .opus, .aac, .webm and .mp4. Both fields are required. For the reference, thirty seconds or more of clean single-speaker speech works best.

**Is this the official Fish Audio SDK?**

No. This is an independent client that wraps the Synexa-hosted endpoint. The official Fish Audio product, API and SDKs are at https://fish.audio.

## Related

- [Fish Audio](https://fish.audio) — official platform, API and open-source releases
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose SDK this client builds on
- [fish-audio/voice-changer on Synexa](https://synexa.ai/explore/fish-audio/voice-changer) — the hosted voice changer endpoint
- [xiaomi/mimo-tts on Synexa](https://synexa.ai/explore/xiaomi/mimo-tts) — text-to-speech with built-in, cloned or described voices

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of Fish Audio. Model weights and trademarks belong to their respective owners.

_Last reviewed: 2026-09-22_
