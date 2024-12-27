import pyttsx3
import os
from google.cloud import texttospeech
import pygame


def speak(text: str):
    try:
        # a = 9/0
        # Initialize Google Cloud TTS client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            "./credentials/service_account.json"
        )
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        audio_file = "output.mp3"
        with open(audio_file, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)

        # Initialize pygame mixer
        pygame.mixer.init()

        try:
            # Load and play the audio file
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait until the audio file has finished playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            # Ensure the mixer is stopped and uninitialized before deleting the file
            pygame.mixer.music.stop()
            pygame.mixer.quit()

            # Optionally, delete the audio file after playing
            try:
                os.remove(audio_file)
            except PermissionError:
                print(
                    f"Error: Unable to delete {audio_file}. Please remove it manually."
                )

    except Exception as e:
        # print(f"Error: {e}")
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.setProperty(
            "voice", voices[1].id
        )  # Change index to choose different voices
        engine.say(text)
        engine.runAndWait()


if __name__ == "__main__":
    speak("Hello world!, I'm Stella")
