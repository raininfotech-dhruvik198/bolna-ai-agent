import asyncio
import aiohttp
import os
from .base_synthesizer import BaseSynthesizer
from bolna.helpers.logger_config import configure_logger
from bolna.helpers.utils import create_ws_data_packet

logger = configure_logger(__name__)

class XTTS_Synthesizer(BaseSynthesizer):
    def __init__(self, voice, language, model="xtts", audio_format="wav", sampling_rate="24000", stream=False, buffer_size=400, **kwargs):
        super().__init__(kwargs.get("task_manager_instance", None), stream)
        self.model = model
        self.voice = voice
        self.language = language
        self.sampling_rate = sampling_rate
        self.audio_format = audio_format
        self.xtts_server_url = os.getenv("XTTS_SERVER_URL", "http://localhost:8000/tts")

    async def __generate_http(self, text):
        payload = {
            "text": text,
            "speaker_wav": self.voice,
            "language": self.language,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.xtts_server_url, json=payload) as response:
                if response.status == 200:
                    data = await response.read()
                    return data
                else:
                    logger.error(f"Error: {response.status} - {await response.text()}")
                    return None

    async def synthesize(self, text):
        audio = await self.__generate_http(text)
        return audio

    async def push(self, message):
        self.internal_queue.put_nowait(message)

    async def generate(self):
        while True:
            message = await self.internal_queue.get()
            meta_info, text = message.get("meta_info"), message.get("data")
            audio = await self.synthesize(text)
            if audio:
                meta_info['format'] = self.audio_format
                yield create_ws_data_packet(audio, meta_info)
            if "end_of_llm_stream" in meta_info and meta_info["end_of_llm_stream"]:
                meta_info["end_of_synthesizer_stream"] = True
                yield create_ws_data_packet(b'\x00', meta_info)
                break
