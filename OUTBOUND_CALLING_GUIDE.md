# Outbound Calling Guide

This guide explains how to use the outbound calling feature to make automated calls from a CSV file for cash-on-delivery (COD) order confirmations.

## Overview

The outbound calling system allows you to:
- Initiate automated calls to a list of recipients from a CSV file.
- Use a conversational AI agent to interact with the recipients.
- Confirm COD orders, handle rescheduling, and update the CSV file with the call outcome.

## Prerequisites

1.  **Docker and Docker Compose**: Ensure you have Docker and Docker Compose installed and running.
2.  **Twilio Account**: You will need a Twilio account with a phone number that can make outbound calls.
3.  **Environment Variables**: Make sure your `.env` file is populated with your Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`) and your other provider keys (e.g., OpenAI, Deepgram, ElevenLabs).
4.  **Running Services**: Start the services using the `./start.sh` script.

## 1. Formatting the CSV File

The system uses a CSV file named `call_list.csv` located in the root directory of the project. The CSV file must have the following columns:

-   `name`: The name of the recipient.
-   `recipient_phone_number`: The phone number of the recipient in E.164 format (e.g., `+15551234567`).
-   `order_id`: The ID of the order to be confirmed.
-   `status`: This column will be updated by the system with the outcome of the call. Leave it empty initially.
-   `reschedule_date`: This column will be updated if the delivery is rescheduled. Leave it empty initially.
-   `reschedule_time`: This column will be updated if the delivery is rescheduled. Leave it empty initially.

**Example `call_list.csv`:**
```csv
name,recipient_phone_number,order_id,status,reschedule_date,reschedule_time
John Doe,+15551234567,ORD123,,,
Jane Smith,+15557654321,ORD124,,,
```

## 2. Creating the Agent

The conversational agent is defined in the `agent_data/cod_confirmation_agent.json` file. To create the agent in the system, you need to send a `POST` request to the `/agent` endpoint of the `bolna-app`.

You can use the following `curl` command to create the agent. This command reads the JSON configuration from the file and sends it to the server.

```bash
curl -X POST http://localhost:5001/agent \
-H "Content-Type: application/json" \
-d @agent_data/cod_confirmation_agent.json
```

The server will respond with a JSON object containing the `agent_id`. **Copy this `agent_id`**, as you will need it to run the outbound calling script.

**Example Response:**
```json
{
  "agent_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "state": "created"
}
```

## 3. Running the Outbound Calling Script

The `outbound_call_manager.py` script is run inside a Docker container to ensure it has access to the same `call_list.csv` file as the telephony server.

To run the script, use the `docker-compose run` command. You will need to pass the `AGENT_ID` you received in the previous step as an environment variable.

**Command:**
```bash
AGENT_ID=<your-agent-id> docker-compose run --rm outbound-caller
```

Replace `<your-agent-id>` with the actual `agent_id` for your COD confirmation agent.

The `outbound-caller` service is configured to use Twilio by default. If you want to use Plivo, you can modify the `command` in the `docker-compose.yml` file for the `outbound-caller` service.

The script will then start making calls to the recipients in the CSV file.

## 4. Viewing the Results

After the calls are completed, the `call_list.csv` file will be updated with the outcomes. You can open the file to see the status of each call.

The `status` column will be updated with one of the following values:
-   `confirmed`
-   `cancelled`
-   `rescheduled`
-   `wrong_person`

If a call was rescheduled, the `reschedule_date` and `reschedule_time` columns will also be updated.

**Example `call_list.csv` after calls:**
```csv
name,recipient_phone_number,order_id,status,reschedule_date,reschedule_time
John Doe,+15551234567,ORD123,confirmed,,
Jane Smith,+15557654321,ORD124,rescheduled,2025-09-13,14:30
```
