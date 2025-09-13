# Bolna: End-to-End Open Source Voice Agents Platform

<p align="center">
  <strong>Build powerful, voice-first conversational assistants with a simple JSON configuration.</strong>
</p>

<h4 align="center">
  <a href="https://discord.gg/59kQWGgnm8">Discord</a> |
  <a href="https://docs.bolna.ai">Hosted Docs</a> |
  <a href="https://bolna.ai">Website</a>
</h4>

<h4 align="center">
  <a href="https://discord.gg/59kQWGgnm8">
      <img src="https://img.shields.io/static/v1?label=Chat%20on&message=Discord&color=blue&logo=Discord&style=flat-square" alt="Discord">
  </a>
  <a href="https://github.com/bolna-ai/bolna/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="Bolna is released under the MIT license." />
  </a>
  <a href="https://github.com/bolna-ai/bolna/blob/main/CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen" alt="PRs welcome!" />
  </a>
</h4>

> [!NOTE]
> We are actively looking for maintainers. If you're passionate about conversational AI, we'd love to have you on board!

## 🚀 Introduction

Bolna is an open-source, end-to-end framework designed for developers to rapidly build, deploy, and manage sophisticated LLM-based voice-driven conversational applications. It serves as a robust orchestration platform that seamlessly integrates various Automatic Speech Recognition (ASR), Large Language Model (LLM), and Text-to-Speech (TTS) providers. With Bolna, you can define complex conversational flows, create specialized agents, and connect them to telephony systems like Twilio and Plivo, all through a declarative JSON configuration.

Whether you're building a customer service bot, a personal assistant, or an interactive voice response (IVR) system, Bolna provides the tools and flexibility you need to create natural and engaging voice experiences.

### Key Features

- **Declarative Agent Configuration**: Define your agent's behavior, tools, and conversational flow using a simple yet powerful JSON structure.
- **Multi-Provider Support**: Integrate with a wide range of ASR, LLM, and TTS providers, including Deepgram, Azure, OpenAI, ElevenLabs, and more.
- **Extensible & Modular**: The modular architecture allows you to easily add new providers, agents, and functionalities.
- **Telephony Integration**: Built-in support for major telephony providers like Twilio and Plivo.
- **State Management**: Robust state and context management to handle complex, multi-turn conversations.
- **Local Development**: A Dockerized local setup for easy development and testing.
- **Scalable & Production-Ready**: Designed to handle real-world traffic and scale with your needs.

## 📂 Repository Structure

Here's a breakdown of the Bolna repository's structure:

```
.
├── bolna/                  # Core application source code
│   ├── agent_manager/      # Manages different types of agents (assistant, task-based)
│   ├── agent_types/        # Defines various agent types (e.g., conversational, summarization)
│   ├── classification/     # Components for classifying user intent or sentiment
│   ├── helpers/            # Utility functions and helper classes
│   ├── input_handlers/     # Handles incoming data from various sources (e.g., telephony)
│   ├── llms/               # Integrations with Large Language Models (LLMs)
│   ├── memory/             # Manages conversation history and state
│   ├── output_handlers/    # Handles outgoing data to various sinks (e.g., telephony)
│   ├── synthesizer/        # Text-to-Speech (TTS) integrations
│   └── transcriber/        # Automatic Speech Recognition (ASR) integrations
├── local_setup/            # Docker-based local development environment
│   ├── dockerfiles/        # Dockerfiles for various services
│   ├── presets/            # Preset configurations and data
│   └── telephony_server/   # Example telephony API servers (Twilio, Plivo)
├── API.md                  # Detailed API documentation
├── LICENSE                 # Project license
├── pyproject.toml          # Project metadata and dependencies
└── requirements.txt        # Python package dependencies
```

## 🧠 Core Concepts

To understand Bolna, it's essential to grasp its core concepts:

- **Agents**: An agent is the primary actor in the Bolna ecosystem. It's a conversational entity that you configure to perform specific tasks. Each agent is defined by its name, type, and a set of tasks it can execute.

- **Tasks**: A task represents a specific goal or a piece of a conversational flow that an agent can perform. For example, a task could be a simple conversation, data extraction, or a summarization. Each task has its own configuration, including the tools it uses and its prompt.

- **Pipelines**: A pipeline is a sequence of tools that process data in a specific order. For example, a typical conversational pipeline would be `transcriber -> llm -> synthesizer`. Bolna's toolchain allows you to define parallel or sequential pipelines, giving you fine-grained control over the data flow.

- **Tools (Providers)**: Tools are the building blocks of pipelines. They are integrations with external services that perform specific functions. Bolna has three main types of tools:
  - **Transcriber (ASR)**: Converts spoken language into text.
  - **LLM**: Processes the transcribed text and generates a response.
  - **Synthesizer (TTS)**: Converts the LLM's text response back into speech.

- **Input/Output Handlers**: These components manage the flow of data to and from external systems. For telephony, the input handler receives audio from the telephony provider, and the output handler sends audio back.

## 🌊 Workflow

A typical Bolna workflow for a voice conversation looks like this:

1.  **Initiation**: A call is initiated through a telephony provider (e.g., Twilio). The provider connects to your Bolna server via a webhook.
2.  **Agent Creation**: You create an agent by sending a `POST` request to the `/agent` endpoint with a JSON configuration. This configuration specifies the agent's name, tasks, and the providers it will use.
3.  **Connection**: The telephony provider establishes a WebSocket connection with the Bolna server.
4.  **Input Handling**: The `input_handler` receives the audio stream from the telephony provider.
5.  **Transcription**: The audio is forwarded to the `transcriber`, which converts it into text.
6.  **LLM Processing**: The transcribed text is sent to the `llm`, which processes it based on the agent's prompt and generates a response.
7.  **Synthesis**: The LLM's text response is sent to the `synthesizer`, which converts it into audio.
8.  **Output Handling**: The `output_handler` streams the synthesized audio back to the telephony provider over the WebSocket connection.
9.  **Termination**: The call is terminated when the conversation ends or when a hangup condition is met.

Here's a visual representation of the workflow:

```mermaid
sequenceDiagram
    participant User
    participant TelephonyProvider as Telephony Provider (e.g., Twilio)
    participant BolnaServer as Bolna Server
    participant Transcriber
    participant LLM
    participant Synthesizer

    User->>+TelephonyProvider: Dials number
    TelephonyProvider->>+BolnaServer: Initiates WebSocket connection
    loop Audio Stream
        User->>TelephonyProvider: Speaks
        TelephonyProvider->>BolnaServer: Streams audio
        BolnaServer->>+Transcriber: Forwards audio
        Transcriber-->>-BolnaServer: Returns transcribed text
        BolnaServer->>+LLM: Sends text
        LLM-->>-BolnaServer: Returns response text
        BolnaServer->>+Synthesizer: Sends response text
        Synthesizer-->>-BolnaServer: Returns synthesized audio
        BolnaServer->>TelephonyProvider: Streams audio back
        TelephonyProvider->>User: Plays audio
    end
    User->>-TelephonyProvider: Hangs up
    TelephonyProvider->>-BolnaServer: Closes connection
```

## 🚀 Getting Started

Follow these steps to set up your local development environment and start building your own voice agents.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (V2)
- An `ngrok` authtoken (for tunneling)

### 1. Clone the Repository

```bash
git clone https://github.com/bolna-ai/bolna.git
cd bolna
```

### 2. Configure Environment Variables

The `local_setup` directory contains a sample environment file, `.env.sample`. You'll need to create a `.env` file from this sample and populate it with your own API keys and credentials.

```bash
cd local_setup
cp .env.sample .env
```

Now, open `.env` and fill in the required values for the ASR, LLM, TTS, and telephony providers you want to use.

### 3. Configure ngrok

You need to add your `ngrok` authtoken to the `ngrok-config.yml` file in the `local_setup` directory.

```yaml
# local_setup/ngrok-config.yml
authtoken: YOUR_NGROK_AUTHTOKEN
version: 2
```

### 4. Start the Services

We've provided a convenient script to get you up and running quickly.

```bash
chmod +x start.sh
./start.sh
```

This script will:
- Check for Docker dependencies.
- Build all the necessary Docker images using BuildKit.
- Start the services (Bolna server, telephony server, ngrok, Redis) in detached mode.

Alternatively, you can build and run the services manually:

```bash
# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build the images
docker compose build

# Run the services
docker compose up -d
```

### 5. Verify the Setup

Once the services are running, you can check the logs to ensure everything is working correctly.

```bash
docker compose logs -f
```

You should see logs from the `bolna-app`, `twilio-app` (or `plivo-app`), and `ngrok` containers. The `ngrok` logs will show you the public URL that you can use to connect your telephony provider to your local Bolna server.

## 🤖 Creating an Agent

Once your local environment is up and running, you can create a new agent by sending a `POST` request to the `/agent` endpoint. The request body should be a JSON object that defines the agent's configuration and prompts.

**Endpoint:** `POST /agent`

### Example Agent Configuration

Here's an example of a simple conversational agent that uses Twilio for telephony, Deepgram for transcription, OpenAI for the LLM, and ElevenLabs for synthesis.

```json
{
  "agent_config": {
      "agent_name": "EchoBot",
      "agent_type": "conversation",
      "tasks": [
          {
              "task_type": "conversation",
              "toolchain": {
                  "execution": "parallel",
                  "pipelines": [
                      [
                          "transcriber",
                          "llm",
                          "synthesizer"
                      ]
                  ]
              },
              "tools_config": {
                  "input": {
                      "provider": "twilio",
                      "format": "wav"
                  },
                  "output": {
                      "provider": "twilio",
                      "format": "wav"
                  },
                  "transcriber": {
                      "provider": "deepgram",
                      "language": "en",
                      "stream": true
                  },
                  "llm_agent": {
                      "provider": "openai",
                      "model": "gpt-4o-mini"
                  },
                  "synthesizer": {
                      "provider": "elevenlabs",
                      "voice": "George",
                      "stream": true
                  }
              }
          }
      ]
  },
  "agent_prompts": {
      "task_1": {
          "system_prompt": "You are a helpful echo assistant. Repeat everything the user says."
      }
  }
}
```

### Key Configuration Parameters

- **`agent_name`**: A unique name for your agent.
- **`agent_type`**: The type of agent (e.g., `conversation`, `extraction`).
- **`tasks`**: A list of tasks the agent can perform.
- **`toolchain`**: Defines the pipelines and the execution order of the tools.
- **`tools_config`**: Specifies the configuration for each tool (input, output, transcriber, llm, synthesizer).
- **`agent_prompts`**: The prompts for each task. The keys should correspond to the task index (e.g., `task_1`).

Upon successful creation, the API will respond with the `agent_id` and the state of the agent.

```json
{
    "agent_id": "your-unique-agent-id",
    "state": "created"
}
```

## 🔌 Supported Providers

Bolna supports a variety of providers for transcription, language modeling, synthesis, and telephony. To use a specific provider, you'll need to set the corresponding environment variables in your `.env` file.

### ASR (Transcriber) Providers

| Provider   | Environment Variable      |
|------------|---------------------------|
| Deepgram   | `DEEPGRAM_AUTH_TOKEN`     |
| Azure      | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` |
| Bodhi      | `BODHI_API_KEY`           |

### LLM Providers

Bolna uses LiteLLM to support a wide range of LLM providers. For most providers, you'll need to set the following environment variables:

| Variable                 | Description                             |
|--------------------------|-----------------------------------------|
| `LITELLM_MODEL_API_KEY`  | API key for the LLM service             |
| `LITELLM_MODEL_API_BASE` | Base URL for the LLM API (if self-hosted) |

For specific providers or configurations, refer to the LiteLLM documentation.

### TTS (Synthesizer) Providers

| Provider   | Environment Variable      | Notes                               |
|------------|---------------------------|-------------------------------------|
| AWS Polly  | -                         | Uses system-wide AWS credentials    |
| ElevenLabs | `ELEVENLABS_API_KEY`      |                                     |
| OpenAI     | `OPENAI_API_KEY`          |                                     |
| Deepgram   | `DEEPGRAM_AUTH_TOKEN`     |                                     |
| Cartesia   | `CARTESIA_API_KEY`        |                                     |
| Smallest   | `SMALLEST_API_KEY`        |                                     |
| Azure      | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` |                                     |
| Rime       | `RIME_API_KEY`            |                                     |
| Sarvam     | `SARVAM_API_KEY`          |                                     |

### Telephony Providers

| Provider | Environment Variables                                    |
|----------|----------------------------------------------------------|
| Twilio   | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` |
| Plivo    | `PLIVO_AUTH_ID`, `PLIVO_AUTH_TOKEN`, `PLIVO_PHONE_NUMBER`       |
| Exotel   | `EXOTEL_API_KEY`, `EXOTEL_API_TOKEN`, `EXOTEL_SUBDOMAIN` |

## 🛠️ Extending Bolna

Bolna is designed to be extensible. If you want to add a new telephony provider (e.g., Vonage, Telnyx), follow these steps:

1.  **Ensure Bidirectional Streaming**: The telephony provider must support bidirectional audio streaming over WebSockets.
2.  **Create an Input Handler**: Add a new file in `bolna/input_handlers/telephony_providers` that extends the `TelephonyInput` class. This class will handle incoming event packets from the provider.
3.  **Create an Output Handler**: Add a new file in `bolna/output_handlers/telephony_providers` that extends the `TelephonyOutput` class. This class will convert the synthesized audio to the provider's required format and stream it back over the WebSocket.
4.  **Create a Telephony Server**: Add a new file in `local_setup/telephony_server` to create a dedicated server for your provider. This server will initiate calls and manage the WebSocket connections. You can use the `twilio_api_server.py` or `plivo_api_server.py` as a reference.

## 🤔 Troubleshooting

- **Docker Build Fails**: Ensure you have Docker BuildKit enabled (`export DOCKER_BUILDKIT=1`). If the build still fails, try pruning your Docker build cache (`docker builder prune`).
- **`ngrok` Tunnel Not Working**: Double-check that your `ngrok` authtoken is correctly set in `local_setup/ngrok-config.yml`. Also, ensure that the `ngrok` container is running (`docker compose ps`).
- **Authentication Errors**: Verify that your API keys and credentials in the `.env` file are correct and have the necessary permissions.
- **WebSocket Connection Fails**: Make sure your telephony provider's webhook is pointing to the correct `ngrok` URL. You can find the URL in the `ngrok` container's logs.

## 💡 Use Cases

Bolna is a versatile framework that can be used to build a wide range of voice-driven applications, including:

- **Customer Service Automation**: Create intelligent voice bots to handle customer queries, provide support, and automate common tasks.
- **Interactive Voice Response (IVR)**: Build dynamic and natural-sounding IVR systems that can understand and respond to user requests in real-time.
- **Personal Assistants**: Develop personalized voice assistants that can help users with tasks like scheduling, reminders, and information retrieval.
- **Data Collection & Surveys**: Conduct automated voice-based surveys and collect data from users in a conversational manner.
- **Sales & Lead Qualification**: Build voice agents that can qualify leads, answer product questions, and schedule demos.
