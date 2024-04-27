import typer

from meta_assistant import logger
from meta_assistant.domain import MicrophoneStream
from meta_assistant.services import (
    SpeechToText,
    TextGenerator,
    TextToSpeech,
    Audio2Face,
    Audio2Chunks,
)

app = typer.Typer(
    name="meta-assistant",
    help="An assistant that uses the Text-To-Speech, the Speech-to-Text, and the Generative AI technologies to interact with the user and to stream the audio to the Nvidia Audio2Face plugin.",
)


@app.command()
def run_meta_assistant(
    microphone_rate: int = typer.Option(
        default=16000, help="The sample rate of the microphone"
    ),
    openai_key: str = typer.Option(
        ...,
        help="The OpenAI API key",
        envvar="OPENAI_KEY",
        show_envvar=True,
    ),
    openai_model: str = typer.Option(
        default="davinci",
        help="The OpenAI model to be used",
        envvar="OPENAI_MODEL",
        show_envvar=True,
    ),
    openai_instruction: str = typer.Option(
        default="",
        help="The instruction to be used by the OpenAI model",
    ),
    grpc_server: str = typer.Option(..., help="The endpoint of the gRPC server"),
):
    """
    Run the meta-assistant
    :return:
    """
    logger.info("Received arguments:")
    logger.info("microphone_rate: {}".format(microphone_rate))
    logger.info("openai_key: {}".format(openai_key))
    logger.info("openai_model: {}".format(openai_model))
    logger.info("openai_instruction: {}".format(openai_instruction))
    logger.info("grpc_server: {}".format(grpc_server))

    # Start the main loop
    while True:
        audio_recording = MicrophoneStream.get_audio(
            sample_rate=microphone_rate, duration=20
        )
        # Process the audio recording
        text = SpeechToText.transcribe(audio=audio_recording)
        logger.info("Transcribed text: {}".format(text))

        # Generate the response
        response = TextGenerator.generate(
            key=openai_key,
            model=openai_model,
            input=text,
            instruction=openai_instruction,
        )
        logger.info("Response: {}".format(response))

        # Generate the speech audio from the response
        audio_synthesized = TextToSpeech.synthesize(text=response)

        # Split the audio into chunks
        audio_chunks, sample_rate = Audio2Chunks.split_audio_to_chunks(
            audio=audio_synthesized
        )

        # Stream the audio to the Audio2Face plugin
        Audio2Face.stream_chunk(
            audio=audio_chunks,
            endpoint=grpc_server,
            sample_rate=sample_rate,
            instance_name="/World/audio2face/PlayerStreaming",
        )


if __name__ == "__main__":
    app()
