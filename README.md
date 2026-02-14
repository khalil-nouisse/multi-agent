# Multi-Agent CRM System

![Project Architecture](assets/diagramme_globale1.png)

## Overview

This project is a sophisticated **Multi-Agent System** designed to assist businesses in managing customer relationships, sales processes, and technical support. Built using **LangChain** and **LangGraph**, it orchestrates specialized AI agents to handle complex user queries and integrate seamlessly with a CRM database.

The core of the system is a **Supervisor Agent** that intelligently routes requests to the appropriate department:
- **Sales Manager**: Handles opportunities, appointments, and estimations.
- **Technical Support**: Manages tickets, resolution estimates, and status checks.
- **Customer Support**: Provides general assistance and status updates.

## Key Features

- **Intelligent Routing**: A Supervisor agent (LLM router) analyzes user intent and directs tasks to the most suitable specialized agent.
- **Stateful Conversation**: Built on `LangGraph`, ensuring context is maintained throughout the interaction.
- **CRM Integration**: Directly interacts with a PostgreSQL database to fetch and update real-time data (Opportunities, Tickets, Client History).
- **Specialized Toolsets**: Each agent is equipped with specific tools (e.g., `opportunity_state`, `ticket_state`, `create_appointment`) to perform concrete actions.
- **Observability**: Integrated with **LangSmith** for full tracing and debugging of agent interactions.

## Architecture

The system follows a star-graph architecture where the **Supervisor** acts as the central hub.

![Supervisor Diagram](assets/supervisor-diagram.png)

1. **User Input**: The user sends a message.
2. **Supervisor Decision**: The Supervisor analyzes the message and decides to:
   - Route to **Sales Manager** if it's about deals or appointments.
   - Route to **Technical Support** if it's about bugs or tickets.
   - Route to **Customer Support** for general service.
   - **Answer Directly** if it's a simple greeting or general question.
3. **Agent Execution**: The selected agent (e.g., Sales) executes its logic, potentially calling tools (DB queries), and returns the result to the Supervisor.
4. **Loop**: The process repeats until the request is satisfied.

## Technology Stack

- **Framework**: [LangChain](https://www.langchain.com/) & [LangGraph](https://python.langchain.com/docs/langgraph)
- **LLM**: OpenAI GPT-3.5 Turbo / GPT-4
- **Database**: PostgreSQL (`psycopg2`)
- **API**: FastAPI (optional integration)
- **Tracing**: LangSmith

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL Database
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/multi-agent-crm.git
cd multi-agent-crm
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your keys:

```ini
OPENAI_API_KEY=sk-your_openai_api_key...
DATABASE_URL=postgresql://user:password@localhost:5432/your_database
LANGCHAIN_API_KEY=lsv2_your_langchain_key...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Multi-Agent-CRM
```

### 5. Database Setup
Ensure your PostgreSQL database is running and has the necessary tables (`status`, `tickets`, `opportunities`). The `databse.py` (database module) handles connections using the `DATABASE_URL`.

## Usage

You can run the main entry point to test the multi-agent graph in the console.

```bash
python main.py
```

### Example Interaction
The default `main.py` is configured to send a test message:
> "Hello there! help me make a coffee" (Simulated user input)

*Note: You can modify `input_data` in `main.py` to test different scenarios.*

## 📂 Project Structure

```
multi-agent/
├── agents/             # Agent definitions (Prompts & Logic)
│   ├── supervisor.py   # Router Agent
│   ├── sales.py        # Sales Agent
│   ├── tech_support.py # Tech Support Agent
│   └── customer.py     # Customer Support Agent
├── tools/              # Tool definitions for each agent
│   ├── sales_tools.py
│   ├── tech_tools.py
│   └── customer_tools.py
├── graph/              # LangGraph construction
│   ├── graph_builder.py
│   └── agents_factory.py
├── communication/      # External communication handlers
├── assets/             # Images and diagrams
├── main.py             # Entry point
├── config.py           # Configuration & Env Loading
├── databse.py          # Database interactions
└── requirements.txt    # Project dependencies
```
