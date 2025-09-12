import asyncio
import os
import json
import aiohttp
import websockets
from dotenv import load_dotenv

from .base_transcriber import BaseTranscriber
from bolna.helpers.logger_config import configure_logger
from bolna.helpers.utils import create_ws_data_packet

logger = configure_logger(__name__)
load_dotenv()


class WhisperTranscriber(BaseTranscriber):
    def __init__(self, telephony_provider, input_queue=None, model='whisper', stream=True, language="en", endpointing="400",
                 sampling_rate="16000", encoding="linear16", output_queue=None, **kwargs):
        super().__init__(input_queue)
        self.endpointing = endpointing
        self.language = language
        self.stream = stream
        self.provider = telephony_provider
        self.heartbeat_task = None
        self.sender_task = None
        self.model = model
        self.sampling_rate = sampling_rate
        self.encoding = encoding
        self.api_key = kwargs.get("transcriber_key", os.getenv('WHISPER_API_KEY'))
        self.whisper_ws_url = kwargs.get("transcriber_ws_url", os.getenv('WHISPER_WEBSOCKET_URL'))
        self.transcriber_output_queue = output_queue
        self.transcription_task = None
        self.websocket_connection = None

    async def _connect(self):
        self.websocket_connection = await websockets.connect(self.whisper_ws_url)
        logger.info("Connected to whisper websocket")

    async def _close(self):
        await self.websocket_connection.close()
        logger.info("Closed whisper websocket connection")

    async def sender(self, ws):
        try:
            while True:
                ws_data_packet = await self.input_queue.get()
                self.meta_info = ws_data_packet.get('meta_info')
                if 'eos' in ws_data_packet['meta_info'] and ws_data_packet['meta_info']['eos'] is True:
                    await self._close()
                    break
                await ws.send(ws_data_packet.get('data'))
        except Exception as e:
            logger.error(f"Error in whisper sender: {e}")

    async def receiver(self, ws):
        async for msg in ws:
            msg = json.loads(msg)
            if msg.get('text'):
                text = msg['text']
                logger.info(f"Received message from whisper: {text}")
                self.transcriber_output_queue.put_nowait(create_ws_data_packet(text, self.meta_info))


    async def transcribe(self):
        try:
            await self._connect()
            self.sender_task = asyncio.create_task(self.sender(self.websocket_connection))
            self.receiver_task = asyncio.create_task(self.receiver(self.websocket_connection))
            await asyncio.gather(self.sender_task, self.receiver_task)
        except Exception as e:
            logger.error(f"Error in whisper transcribe: {e}")
        finally:
            if self.sender_task:
                self.sender_task.cancel()
            if self.receiver_task:
                self.receiver_task.cancel()
            if self.websocket_connection:
                await self._close()
