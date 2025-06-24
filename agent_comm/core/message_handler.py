"""
Message Handler - Handles message routing and processing logic
"""

from typing import Dict, List, Any, Optional, Tuple
from .state_manager import StateManager


class MessageHandler:
    """Handles message processing and routing between agents"""
    
    def __init__(self):
        self.state_manager = StateManager()
    
    def send_message(self, from_agent: str, to_agent: str, message: str, 
                    agent_name: str = None, agent_type: str = "custom") -> Tuple[bool, str]:
        """
        Send a message from one agent to another
        
        Returns:
            Tuple of (success: bool, result_message: str)
        """
        try:
            # Register agents if not exists
            self._ensure_agent_registered(from_agent, agent_name or from_agent, agent_type)
            self._ensure_agent_registered(to_agent, to_agent, "custom")
            
            # Update sender activity
            self.state_manager.update_agent_activity(from_agent)
            
            # Find or create conversation
            conv_id = self.state_manager.find_conversation_between_agents(from_agent, to_agent)
            if not conv_id:
                conv_id = self.state_manager.create_conversation(from_agent, to_agent)
            
            # Add message to conversation
            msg_id = self.state_manager.add_message(conv_id, from_agent, to_agent, message)
            
            return True, f"Message sent successfully to {to_agent}. Conversation: {conv_id}, Message: {msg_id}"
            
        except Exception as e:
            return False, f"Error sending message: {str(e)}"
    
    def check_messages(self, agent_id: str, agent_name: str = None, 
                      agent_type: str = "custom") -> Tuple[bool, str]:
        """
        Check for pending messages for an agent
        
        Returns:
            Tuple of (success: bool, result_message: str)
        """
        try:
            # Register agent if not exists
            self._ensure_agent_registered(agent_id, agent_name or agent_id, agent_type)
            
            # Update agent activity
            self.state_manager.update_agent_activity(agent_id)
            
            # Get pending messages
            pending_messages = self.state_manager.get_pending_messages_for_agent(agent_id)
            
            if not pending_messages:
                return True, f"No new messages for {agent_id}."
            
            # Process messages
            result_messages = []
            for msg_data in pending_messages:
                conv_id = msg_data["conversation_id"]
                message = msg_data["message"]
                
                # Mark as delivered
                self.state_manager.mark_message_delivered(conv_id, message["id"])
                
                # Format message for display
                from_agent = message["from"]
                content = message["content"]
                timestamp = message["timestamp"]
                
                result_messages.append(f"From {from_agent} ({timestamp}): {content}")
            
            # Combine all messages
            if len(result_messages) == 1:
                return True, f"You have a new message:\n\n{result_messages[0]}\n\nPlease respond to this message."
            else:
                messages_text = "\n\n".join([f"{i+1}. {msg}" for i, msg in enumerate(result_messages)])
                return True, f"You have {len(result_messages)} new messages:\n\n{messages_text}\n\nPlease respond to these messages."
                
        except Exception as e:
            return False, f"Error checking messages: {str(e)}"
    
    def get_conversation_history(self, agent1: str, agent2: str, limit: int = 20) -> Tuple[bool, str]:
        """
        Get conversation history between two agents
        
        Returns:
            Tuple of (success: bool, formatted_conversation: str)
        """
        try:
            conv_id = self.state_manager.find_conversation_between_agents(agent1, agent2)
            if not conv_id:
                return True, f"No conversation found between {agent1} and {agent2}."
            
            conversation = self.state_manager.get_conversation(conv_id)
            if not conversation:
                return True, f"Conversation {conv_id} not found."
            
            messages = conversation.get("messages", [])
            
            # Get recent messages (limit)
            recent_messages = messages[-limit:] if len(messages) > limit else messages
            
            if not recent_messages:
                return True, f"No messages in conversation between {agent1} and {agent2}."
            
            # Format conversation
            formatted_messages = []
            for msg in recent_messages:
                from_agent = msg["from"]
                content = msg["content"]
                timestamp = msg["timestamp"]
                status = msg["status"]
                
                formatted_messages.append(f"[{timestamp}] {from_agent}: {content} [{status}]")
            
            conversation_text = "\n".join(formatted_messages)
            
            return True, f"Conversation between {agent1} and {agent2}:\n\n{conversation_text}"
            
        except Exception as e:
            return False, f"Error getting conversation history: {str(e)}"
    
    def list_all_agents(self) -> Tuple[bool, str]:
        """
        List all registered agents
        
        Returns:
            Tuple of (success: bool, agents_list: str)
        """
        try:
            agents = self.state_manager.get_all_agents()
            
            if not agents:
                return True, "No agents registered yet."
            
            # Format agents list
            agent_list = []
            for agent_id, agent_info in agents.items():
                name = agent_info.get("name", agent_id)
                agent_type = agent_info.get("type", "unknown")
                status = agent_info.get("status", "unknown")
                last_active = agent_info.get("last_active", "never")
                
                agent_list.append(f"• {agent_id} ({name}) - Type: {agent_type}, Status: {status}, Last active: {last_active}")
            
            agents_text = "\n".join(agent_list)
            
            return True, f"Registered agents ({len(agents)}):\n\n{agents_text}"
            
        except Exception as e:
            return False, f"Error listing agents: {str(e)}"
    
    def get_pending_calls_info(self) -> Tuple[bool, str]:
        """
        Get information about current pending tool calls
        
        Returns:
            Tuple of (success: bool, pending_info: str)
        """
        try:
            pending_calls = self.state_manager.get_pending_calls()
            
            if not pending_calls:
                return True, "No pending tool calls."
            
            # Format pending calls
            pending_list = []
            for agent_id, call_info in pending_calls.items():
                message = call_info.get("message", "No message")
                timestamp = call_info.get("timestamp", "unknown")
                
                pending_list.append(f"• {agent_id}: {message[:50]}{'...' if len(message) > 50 else ''} ({timestamp})")
            
            pending_text = "\n".join(pending_list)
            
            return True, f"Pending tool calls ({len(pending_calls)}):\n\n{pending_text}"
            
        except Exception as e:
            return False, f"Error getting pending calls info: {str(e)}"
    
    def _ensure_agent_registered(self, agent_id: str, agent_name: str, agent_type: str):
        """Ensure agent is registered in the system"""
        agent_info = self.state_manager.get_agent_info(agent_id)
        if not agent_info:
            self.state_manager.register_agent(agent_id, agent_name, agent_type)
    
    def parse_agent_id(self, agent_input: str) -> Tuple[str, str, str]:
        """
        Parse agent input to extract ID, name, and type
        
        Examples:
            "claude_001" -> ("claude_001", "claude_001", "custom")
            "claude:Claude Sonnet" -> ("claude", "Claude Sonnet", "claude")
            "chatgpt:ChatGPT-4:openai" -> ("chatgpt", "ChatGPT-4", "openai")
        """
        parts = agent_input.split(":")
        
        if len(parts) == 1:
            # Just ID
            agent_id = parts[0].strip()
            return agent_id, agent_id, "custom"
        elif len(parts) == 2:
            # ID:Name
            agent_id = parts[0].strip()
            agent_name = parts[1].strip()
            # Infer type from ID
            agent_type = self._infer_agent_type(agent_id)
            return agent_id, agent_name, agent_type
        elif len(parts) == 3:
            # ID:Name:Type
            agent_id = parts[0].strip()
            agent_name = parts[1].strip()
            agent_type = parts[2].strip()
            return agent_id, agent_name, agent_type
        else:
            # Fallback
            return agent_input, agent_input, "custom"
    
    def _infer_agent_type(self, agent_id: str) -> str:
        """Infer agent type from agent ID"""
        agent_id_lower = agent_id.lower()
        
        if "claude" in agent_id_lower:
            return "claude"
        elif "chatgpt" in agent_id_lower or "gpt" in agent_id_lower:
            return "chatgpt"
        elif "gemini" in agent_id_lower:
            return "gemini"
        elif "copilot" in agent_id_lower:
            return "copilot"
        else:
            return "custom" 