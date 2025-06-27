# Agent Communication System

A sophisticated multi-agent communication framework that enables seamless collaboration between AI agents through MCP (Model Context Protocol) tools, with support for real-time message routing, admin control, and dual-language operation.

## 🌟 Features

- **Multi-Agent Communication**: Enable Agent 1 and Agent 2 to communicate efficiently
- **Admin Control System**: Absolute priority commands with SOURCE tag authority
- **Real-time Message Routing**: Smart delivery and manual routing options
- **Dual Language Support**: Vietnamese and English rule sets
- **Advanced UI Controller**: Comprehensive interface for message management
- **File & Image Attachments**: Support for mixed content communication
- **Workspace-Aware**: Intelligent path processing for different workspaces

## 📋 Prerequisites

- Python
- MCP-compatible AI environment (e.g., Claude, Cursor)
- Git for repository cloning

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/mcp-server-agent-comm.git
cd mcp-server-agent-comm
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. MCP Server Configuration

Add the following configuration to your MCP settings:

```json
{
  "agent_chat_1": {
    "command": "python",
    "args": ["E:/MCP-servers-github/Utils/mcp_server_agent1.py"],
    "stdio": true,
    "enabled": true
  },
  "agent_chat_2": {
    "command": "python",
    "args": ["E:/MCP-servers-github/Utils/mcp_server_agent2.py"],
    "stdio": true,
    "enabled": true
  }
}
```

**Note**: Update the path `E:/MCP-servers-github/Utils/` to match your actual installation directory.

## 📚 Rule Configuration

### Language Options

Choose one of the rule files based on your preferred language:

- **Vietnamese**: `rule_for_AI_VI.txt`
- **English**: `rule_for_AI_EN.txt`

### Setup in Cursor

1. Open Cursor settings
2. Navigate to "Rules for AI" section
3. Copy and paste the content of your chosen rule file
4. Save the configuration

![image](https://github.com/user-attachments/assets/7733c8fe-8418-4d17-b1b3-07cc9ca4aa92)

## 🚀 Usage

### Step 1: Start Controller UI

Open your terminal/command prompt and run:

```bash
python E:\MCP-servers-github\Utils\main_controller.py
```

**Note**: Replace `E:\MCP-servers-github\Utils\` with your actual installation path.

The Controller UI will open, allowing you to monitor and control agent communication.

![image](https://github.com/user-attachments/assets/62c4ec9a-0113-4e11-8e98-c728a2a06927)

Feature "AI Chat" -> user can chat with all waiting agent.

![image](https://github.com/user-attachments/assets/036ebabb-5147-4013-a95a-59799c4827fe)

### Step 2: Setup Agents in Cursor

1. **Open Two Tabs**: Create two separate chat tabs in Cursor
![image](https://github.com/user-attachments/assets/6327fb91-e927-423b-b4c6-9cf44ff867ff)
2. **Tab 1 - Agent 1**: Type activation command to start Agent 1
3. **Tab 2 - Agent 2**: Type activation command to start Agent 2
4. **Execute Tools**: Allow AI to call the MCP server agent chat tools
5. **Monitor Controller**: Check Controller UI for registered agents
6. **Route Messages**: Use Controller UI to manage message delivery

### Activation Commands

#### For AI Interaction Mode:
- **Vietnamese**: `start ai_interaction`
- **English**: `start ai_interaction`

#### For Agent Communication Mode:
- **Vietnamese**: `start agent chat 1` or `start agent chat 2`
- **English**: `start agent chat 1` or `start agent chat 2`

### Communication Flow

1. **Agent Registration**: Agents register with their respective tools
2. **Message Routing**: Controller UI manages message delivery
3. **Priority System**: Admin commands (SOURCE=admin) have absolute priority
4. **Collaboration**: Agents discuss and confirm execution plans for admin tasks

### Detailed Workflow

#### Initial Setup:
1. Start Controller UI with `python main_controller.py`
2. Open Cursor with two chat tabs
3. Activate Agent 1 in Tab 1: `start agent chat 1`
4. Activate Agent 2 in Tab 2: `start agent chat 2`
5. Verify both agents appear in Controller UI "Waiting Agents" section

#### Message Communication:
1. Send message from Agent 1 (will appear in message queue)
2. Use Controller UI to route message to Agent 2
3. Agent 2 receives and can respond
4. Continue conversation through Controller UI routing

#### Admin Controls:
- Send admin messages with absolute priority
- Use "Smart Delivery" for automatic routing
- Monitor real-time agent status
- Clear data when needed

### Admin Controls

- **Absolute Authority**: Admin messages override all agent activities
- **Smart Delivery**: Automatic routing to available agents
- **Manual Routing**: Precise control over message delivery
- **Real-time Monitoring**: Live status of waiting agents and message queue

## 🏗️ Project Structure

```
Utils/
├── agent_comm/
│   ├── core/                    # Core system components
│   │   ├── config_manager.py    # Configuration management
│   │   ├── flow_manager.py      # Message flow control
│   │   ├── message_handler.py   # Message processing
│   │   └── state_manager.py     # System state management
│   ├── ui/                      # User interface components
│   │   ├── controller_ui.py     # Main controller interface
│   │   └── styles.py           # UI styling
│   ├── chat_ui/                # Chat interface system
│   └── shared_data/            # Persistent data storage
├── mcp_server_agent1.py        # Agent 1 MCP server
├── mcp_server_agent2.py        # Agent 2 MCP server
├── rule_for_AI_VI.txt          # Vietnamese rules
├── rule_for_AI_EN.txt          # English rules
└── README.md                   # This file
```

## 🎯 Key Components

### Agent Chat Tools
- **mcp_agent_chat_1_agent_chat_1_tool**: Communication tool for Agent 1
- **mcp_agent_chat_2_agent_chat_2_tool**: Communication tool for Agent 2

### Controller Features
- Message queue management
- Agent status monitoring
- Smart delivery system
- File and image attachment support
- Real-time refresh capability

### Rule System
- **SOURCE Tag Authority**: admin = absolute priority, agent = standard
- **Initialization Rules**: Keyword-based activation system
- **Workflow Compliance**: Mandatory tool recall and thinking blocks
- **Language Consistency**: Vietnamese or English throughout communication

## 🔧 Advanced Features

### Message Types
- **Text Messages**: Standard communication
- **File Attachments**: Document and code sharing
- **Image Support**: Visual content communication
- **Mixed Content**: Combined text, files, and images

### Priority System
- **Admin Commands**: Immediate execution, override all activities
- **Agent Messages**: Standard peer-to-peer communication
- **Collaboration Required**: Agents must discuss admin task execution

### UI Controller
- **Real-time Updates**: 1.5-second refresh intervals
- **Multi-selection**: Batch operations on messages
- **Smart Routing**: Automatic agent selection
- **Status Tracking**: Comprehensive system monitoring

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   - Verify Python path in configuration
   - Check file permissions
   - Ensure all dependencies are installed

2. **Agents Not Communicating**
   - Confirm both agents are registered
   - Check controller UI for waiting agents
   - Verify rule file is properly configured

3. **Message Queue Issues**
   - Use "Clear All Data" in controller UI
   - Restart MCP servers
   - Check shared_data directory permissions

### Support

For issues and questions:
1. Check the troubleshooting section above
2. Review system logs in shared_data directory
3. Verify MCP server configuration
