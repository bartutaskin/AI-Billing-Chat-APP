# SE4458 AI Billing Monorepo

This repository combines the following three components of the AI-powered billing system:

- **AI-CHAT-APP**: Frontend chat application where users can interact with the system
- **AI-AGENT**: Backend service with an AI agent that interprets user inputs and generates requests
- **API-GATEWAY**: API layer that connects the AI agent with billing services

Each component is maintained in its own directory:
📁 AI-CHAT-APP
📁 AI-AGENT
📁 API-GATEWAY

## 📦 Structure

| Folder         | Description                                  |
|----------------|----------------------------------------------|
| `AI-CHAT-APP/` | Web app for user interaction via chat        |
| `AI-AGENT/`    | AI logic using an LLM to process messages    |
| `API-GATEWAY/` | Gateway that routes requests to billing APIs |

## 📄 Documentation

Each folder contains its **own detailed `README.md`** with setup and usage instructions.

Please refer to:
- [`AI-CHAT-APP/README.md`](./AI-CHAT-APP/README.md)
- [`AI-AGENT/README.md`](./AI-AGENT/README.md)
- [`API-GATEWAY/README.md`](./API-GATEWAY/README.md)

for specific details on how to run and develop each component.
