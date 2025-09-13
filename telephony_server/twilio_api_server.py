import os
import json
import requests
import uuid
import urllib.parse
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
import csv
import shutil
from filelock import FileLock

app = FastAPI()
load_dotenv()
port = 8001

twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(twilio_account_sid, twilio_auth_token)


def populate_ngrok_tunnels():
    response = requests.get("http://ngrok:4040/api/tunnels")  # ngrok interface
    telephony_url, bolna_url = None, None

    if response.status_code == 200:
        data = response.json()

        for tunnel in data['tunnels']:
            if tunnel['name'] == 'twilio-app':
                telephony_url = tunnel['public_url']
            elif tunnel['name'] == 'bolna-app':
                bolna_url = tunnel['public_url'].replace('https:', 'wss:')

        return telephony_url, bolna_url
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")


@app.post('/call')
async def make_call(request: Request):
    try:
        call_details = await request.json()
        agent_id = call_details.get('agent_id', None)
        context_data = call_details.get('context_data', None)

        if not agent_id:
            raise HTTPException(status_code=404, detail="Agent not provided")

        if not call_details or "recipient_phone_number" not in call_details:
            raise HTTPException(status_code=404, detail="Recipient phone number not provided")

        telephony_host, bolna_host = populate_ngrok_tunnels()

        print(f'telephony_host: {telephony_host}')
        print(f'bolna_host: {bolna_host}')

        connect_url = f"{telephony_host}/twilio_connect?bolna_host={bolna_host}&agent_id={agent_id}"
        if context_data:
            encoded_context = urllib.parse.quote(json.dumps(context_data))
            connect_url += f"&context_data={encoded_context}"

        try:
            call = twilio_client.calls.create(
                to=call_details.get('recipient_phone_number'),
                from_=twilio_phone_number,
                url=connect_url,
                method="POST",
                record=True
            )
        except Exception as e:
            print(f'make_call exception: {str(e)}')

        return PlainTextResponse("done", status_code=200)

    except Exception as e:
        print(f"Exception occurred in make_call: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post('/twilio_connect')
async def twilio_connect(bolna_host: str = Query(...), agent_id: str = Query(...), context_data: str = Query(None)):
    try:
        response = VoiceResponse()

        connect = Connect()
        bolna_websocket_url = f'{bolna_host}/chat/v1/{agent_id}'
        if context_data:
            bolna_websocket_url += f"?context_data={context_data}"

        connect.stream(url=bolna_websocket_url)
        print(f"websocket connection done to {bolna_websocket_url}")
        response.append(connect)

        return PlainTextResponse(str(response), status_code=200, media_type='text/xml')

    except Exception as e:
        print(f"Exception occurred in twilio_callback: {e}")


@app.post('/call_status')
async def call_status(request: Request):
    try:
        call_outcome = await request.json()

        recipient_phone_number = call_outcome.get("recipient_phone_number")
        if not recipient_phone_number:
            raise HTTPException(status_code=400, detail="Recipient phone number not provided in the payload.")

        csv_file_path = "call_list.csv"
        lock_path = "call_list.csv.lock"
        lock = FileLock(lock_path, timeout=10)

        with lock:
            temp_file_path = "call_list.tmp"
            with open(csv_file_path, 'r', newline='') as csvfile, open(temp_file_path, 'w', newline='') as tempfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(tempfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    if row["recipient_phone_number"] == recipient_phone_number:
                        row["status"] = call_outcome.get("status", row["status"])
                        if "reschedule_date" in call_outcome:
                            row["reschedule_date"] = call_outcome["reschedule_date"]
                        if "reschedule_time" in call_outcome:
                            row["reschedule_time"] = call_outcome["reschedule_time"]
                    writer.writerow(row)

            shutil.move(temp_file_path, csv_file_path)

        return PlainTextResponse("done", status_code=200)

    except Exception as e:
        print(f"Exception occurred in call_status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
