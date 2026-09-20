        """Minimal Fish Audio example: create one prediction and print the output URL(s)."""
        import fish_audio_api

        output = fish_audio_api.run({
    "audio": "https://example.com/input.png",
    "reference_audio": "https://example.com/input.png"
})
        print(output)
