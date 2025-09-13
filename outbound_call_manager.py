import csv
import requests
import argparse

# The URL of the Telephony application server (Twilio or Plivo)
TELEPHONY_APP_URL = "http://twilio-app:8001/call"  # Default to Twilio

def make_outbound_calls(agent_id: str, csv_file_path: str, telephony_provider: str):
    """
    Reads a CSV file and initiates outbound calls for each recipient.

    Args:
        agent_id (str): The ID of the agent to be used for the calls.
        csv_file_path (str): The path to the CSV file containing recipient data.
    """
    try:
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                recipient_phone_number = row.get("recipient_phone_number")
                if not recipient_phone_number:
                    print(f"Skipping row due to missing 'recipient_phone_number': {row}")
                    continue

                payload = {
                    "agent_id": agent_id,
                    "recipient_phone_number": recipient_phone_number,
                    "context_data": {
                        "recipient_name": row.get("name"),
                        "order_id": row.get("order_id")
                    }
                }

                print(f"Initiating call to {recipient_phone_number} ({row.get('name')}) with agent {agent_id}...")

                try:
                    if telephony_provider == "plivo":
                        url = "http://plivo-app:8002/call"
                    else:
                        url = TELEPHONY_APP_URL

                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        print(f"Successfully initiated call to {recipient_phone_number} via {telephony_provider}")
                    else:
                        print(f"Failed to initiate call to {recipient_phone_number}. Status code: {response.status_code}, Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred while trying to initiate a call to {recipient_phone_number}: {e}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outbound Call Manager")
    parser.add_argument("--agent_id", type=str, required=True, help="The ID of the agent to be used for the calls.")
    parser.add_argument("--csv_file", type=str, default="call_list.csv", help="The path to the CSV file containing recipient data.")
    parser.add_argument("--telephony_provider", type=str, default="twilio", choices=["twilio", "plivo"], help="The telephony provider to use (twilio or plivo).")

    args = parser.parse_args()

    make_outbound_calls(args.agent_id, args.csv_file, args.telephony_provider)
