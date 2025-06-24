# 🤖 Agent Communication System

A sophisticated MCP (Model Context Protocol) server enabling **controlled communication** between multiple AI agents through user-managed message routing.

## 🎯 **System Overview**

### **Core Concept**
Instead of direct agent-to-agent communication, this system implements **user-controlled message routing**:

1. **Agents call MCP tools** → Register as "waiting" 
2. **User runs controller** → Sees waiting agents & pending messages
3. **User clicks buttons** → Delivers messages between agents
4. **Agents receive responses** → Continue conversation naturally

### **Architecture**
```
Claude → agent_chat_1_tool() → WAITING (promise-like)
                                    ↓
                              [JSON Storage]
                                    ↓
ChatGPT → agent_chat_2_tool() → WAITING (promise-like)
                                    ↓
User → python main_controller.py → Controller UI → Deliver Messages
                                    ↓
Claude ← receives ChatGPT's message ← RESOLVED (promise)
                                    ↓
ChatGPT ← receives Claude's message ← RESOLVED (promise)
```

## 🛠️ **Components**

### **1. MCP Tools (for AI Agents)**
- **`agent_chat_1_tool`** - For Claude/Agent 1
- **`agent_chat_2_tool`** - For ChatGPT/Gemini/Agent 2

### **2. Controller UI (for User)**  
- **`python main_controller.py`** - Standalone controller application
- PyQt5 interface with real-time updates
- Message queue management
- Click-to-deliver functionality

### **3. Shared Storage**
- **`waiting_agents.json`** - Agents waiting for responses
- **`message_queue.json`** - Messages pending delivery
- **`conversation_flow.json`** - Flow state management

## 🚀 **Quick Start**

### **Step 1: Start MCP Server**
```bash
python mcp_server.py
```

### **Step 2: Agents Call Tools**
Claude calls:
```python
agent_chat_1_tool("claude_001", "Hello ChatGPT! How are you?")
# → Blocks waiting for response
```

ChatGPT calls:
```python  
agent_chat_2_tool("chatgpt_001", "Hi Claude! I'm doing well, thanks!")
# → Blocks waiting for response
```

### **Step 3: User Controls Flow**
```bash
python main_controller.py
```
- UI opens showing waiting agents & messages
- Click on messages to see details
- Click "Send to Agent 1/2" to deliver
- Agents receive responses and continue

## 📋 **Usage Examples**

### **Basic Agent Chat**
```python
# Claude starts conversation
result1 = agent_chat_1_tool("claude_001", "What's 2+2?")
# Waits until user delivers ChatGPT's response via controller

# ChatGPT responds  
result2 = agent_chat_2_tool("chatgpt_001", "2+2 equals 4!")
# Waits until user delivers Claude's next message via controller
```

### **Controller Commands**
```bash
python main_controller.py           # Main UI
python main_controller.py --status  # Show status only
python main_controller.py --cleanup # Clean old data
python main_controller.py --help    # Show help
```

## 🧪 **Testing & Demo**

### **Run Complete Demo**
```bash
python test_final_workflow.py
```
This will:
1. Start Claude and ChatGPT agents in background
2. Show you when to run the controller
3. Guide you through message delivery
4. Complete the full conversation cycle

### **Quick Status Check**
```bash  
python test_final_workflow.py --status
```

## 🎮 **Controller UI Features**

### **Waiting Agents Panel**
- Shows agents currently waiting for messages
- Color-coded by agent type (Agent 1 vs Agent 2)
- Status indicators (waiting/delivered)
- Click to see agent details

### **Message Queue Panel**
- Lists all pending messages
- Preview of message content
- Delivery status tracking
- Click to see full message

### **Delivery Actions**
- **"Send to Agent 1"** - Deliver to Claude/Agent 1
- **"Send to Agent 2"** - Deliver to ChatGPT/Agent 2
- **Auto-refresh** - Updates every 3 seconds
- **Cleanup tools** - Remove old data

## 🔧 **Technical Details**

### **Promise-like Behavior**
Tools use `wait_for_delivery()` with timeout:
```python
waiting_id = flow_manager.register_waiting_agent("agent_chat_1", agent_id, message)
delivered_message = flow_manager.wait_for_delivery(waiting_id, timeout=300)
```

### **Thread-safe Storage**
All JSON operations use threading locks:
```python
with self._lock:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### **Auto-cleanup**
Automatic removal of old data:
- Waiting agents older than 24 hours
- Delivered messages older than 24 hours
- Failed/timeout sessions

## 📁 **File Structure**
```
agent_comm/
├── core/
│   ├── flow_manager.py      # Core state management
│   ├── state_manager.py     # JSON persistence
│   ├── message_handler.py   # Message routing
│   └── conversation.py      # Conversation logic
├── ui/
│   ├── controller_ui.py     # Main controller interface
│   └── simple_ui.py         # Basic UI components
├── agent_chat_tools.py      # MCP tool implementations
└── shared_data/             # JSON storage directory

main_controller.py           # Standalone controller app
mcp_server.py               # MCP server entry point
test_final_workflow.py      # Demo & testing
```

## 🎯 **Use Cases**

### **1. Controlled AI Conversations**
- Debate between Claude and ChatGPT on specific topics
- User moderates and controls conversation flow
- Prevents runaway conversations

### **2. Multi-Agent Problem Solving**
- Agent 1 proposes solutions
- User reviews and forwards to Agent 2  
- Agent 2 critiques and improves
- Iterative refinement under user control

### **3. Research & Development**
- Test different prompting strategies
- Compare agent responses
- Study conversation patterns
- Control experimental conditions

## ⚡ **Advantages**

✅ **User Control** - Complete control over message flow  
✅ **No Runaway** - Prevents infinite agent loops  
✅ **Transparent** - See all messages before delivery  
✅ **Moderated** - Act as conversation moderator  
✅ **Debuggable** - Clear visibility into agent states  
✅ **Flexible** - Support any number of agent types  
✅ **Persistent** - Conversation history saved  

## 🚦 **Status Indicators**

- **🤖1** - Agent 1 (Claude) 
- **🤖2** - Agent 2 (ChatGPT/Gemini)
- **⏳** - Message pending delivery
- **✅** - Message delivered
- **🎮** - Controller ready
- **💤** - No activity

## 🎉 **Success Metrics**

The system is working correctly when:
1. Agents call tools and show "waiting" status
2. Controller UI displays waiting agents and messages
3. User clicks deliver → Agents receive responses
4. Conversation continues in controlled cycles
5. No timeout errors or lost messages

---

**🔗 Built with MCP (Model Context Protocol)**  
**🎨 UI powered by PyQt5**  
**📦 State managed via JSON persistence**  
**🔄 Promise-like async tool behavior** 