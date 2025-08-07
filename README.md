# Agent Communication System

A flexible MCP-based framework for coordinating multiple autonomous agents. The
current design focuses on collaborative code editing: when the server is
invoked it spawns one agent per supplied Python file and initiates a group
conversation where the agents plan and implement changes together. Each agent is
restricted to editing its assigned file through a `FileScopedEditor`, ensuring
clear ownership and accountability.

## Features
- **Dynamic group chats** – conversations can include any number of agents.
- **File-scoped responsibilities** – every agent can only read and modify its
  designated file.
- **Broadcast messaging** – `StateManager` and `MessageHandler` track delivery to
  all participants and manage conversation history.
- **Controller UI** – optional interface (`main_controller.py`) to inspect
  conversations, pending messages and manually route communication.
- **MCP tooling** – exposes an `agent_group_chat_tool` usable by clients that
  speak the Model Context Protocol.

## Installation
1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/your-repo/mcp-server-agent-comm.git
   cd mcp-server-agent-comm
   pip install -r requirements.txt
   ```

2. (Optional) run `python main_controller.py` to open the controller UI.

## Running the Group Chat Server
The server entry point is `mcp_server_group_chat.py`. Pass Python files whose
agents should participate in the session:
```bash
python mcp_server_group_chat.py path/to/agent_a.py path/to/agent_b.py
```
Alternatively, set the `GROUP_CHAT_AGENT_FILES` environment variable with a
comma-separated list of files before starting the server.

The server registers the `agent_group_chat_tool`. Clients can call this tool
with a list of file paths and an initial message to create a conversation among
those agents:
```json
{
  "file_agents": ["agents/a.py", "agents/b.py"],
  "initial_message": "Implement the new API endpoint"
}
```
Each file name becomes the agent ID; the tool binds a `FileScopedEditor` to the
agent so it can only modify its own file. Messages are broadcast to all
participants and stored with per-recipient delivery status.

## Project Structure
```
agent_comm/
├── agent_chat_tools.py   # Contains agent_group_chat_tool and controller tool
├── core/
│   ├── state_manager.py  # Group conversation and registration logic
│   ├── message_handler.py# Broadcast messaging utilities
│   ├── file_scoped_editor.py # File-scoped read/modify wrapper
│   └── flow_manager.py   # Tracks conversations and message queues
├── ui/                   # Controller UI components
└── ...

mcp_server_group_chat.py  # MCP entry point for group chat sessions
main_controller.py        # Optional UI server
rule_for_AI_EN.txt        # English rule set (example)
rule_for_AI_VI.txt        # Vietnamese rule set (example)
```

## Usage Notes
- Agents communicate exclusively through the group conversation. The controller
  can observe and redirect messages but does not alter conversation content.
- Additional MCP clients (e.g., editors) can connect and issue tool calls to
  monitor progress or inject new tasks.

## License
MIT
