"""
Conversation Manager - Handles conversation flow and logic
"""

from typing import Dict, List, Any, Optional, Tuple
from .state_manager import StateManager
from .message_handler import MessageHandler


class ConversationManager:
    """Manages conversation flow and multi-agent interactions"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.message_handler = MessageHandler()
    
    def start_conversation(self, agent1: str, agent2: str, initial_message: str = None) -> Tuple[bool, str]:
        """
        Start a new conversation between two agents
        
        Returns:
            Tuple of (success: bool, result_message: str)
        """
        try:
            # Check if conversation already exists
            existing_conv = self.state_manager.find_conversation_between_agents(agent1, agent2)
            
            if existing_conv:
                return True, f"Conversation already exists between {agent1} and {agent2}: {existing_conv}"
            
            # Create new conversation
            conv_id = self.state_manager.create_conversation(agent1, agent2)
            
            # Add initial message if provided
            if initial_message:
                self.state_manager.add_message(conv_id, agent1, agent2, initial_message)
                return True, f"New conversation started: {conv_id}. Initial message sent from {agent1} to {agent2}."
            else:
                return True, f"New conversation started: {conv_id} between {agent1} and {agent2}."
                
        except Exception as e:
            return False, f"Error starting conversation: {str(e)}"
    
    def get_conversation_summary(self, conv_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get summary information about a conversation
        
        Returns:
            Tuple of (success: bool, summary_data: Dict)
        """
        try:
            conversation = self.state_manager.get_conversation(conv_id)
            if not conversation:
                return False, {"error": f"Conversation {conv_id} not found"}
            
            summary = {
                "conversation_id": conv_id,
                "participants": conversation.get("participants", []),
                "created_at": conversation.get("created_at"),
                "last_update": conversation.get("last_update"),
                "total_messages": conversation.get("message_count", 0),
                "last_message": None,
                "pending_messages": 0
            }
            
            messages = conversation.get("messages", [])
            if messages:
                last_msg = messages[-1]
                summary["last_message"] = {
                    "from": last_msg.get("from"),
                    "content": last_msg.get("content", "")[:100] + "..." if len(last_msg.get("content", "")) > 100 else last_msg.get("content", ""),
                    "timestamp": last_msg.get("timestamp")
                }
                
                # Count pending messages
                pending_count = sum(1 for msg in messages if msg.get("status") == "pending")
                summary["pending_messages"] = pending_count
            
            return True, summary
            
        except Exception as e:
            return False, {"error": f"Error getting conversation summary: {str(e)}"}
    
    def get_all_conversations_summary(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Get summary of all conversations
        
        Returns:
            Tuple of (success: bool, conversations_list: List[Dict])
        """
        try:
            conversations = self.state_manager.get_all_conversations()
            summaries = []
            
            for conv_id, conv_data in conversations.items():
                success, summary = self.get_conversation_summary(conv_id)
                if success:
                    summaries.append(summary)
            
            # Sort by last update (most recent first)
            summaries.sort(key=lambda x: x.get("last_update", ""), reverse=True)
            
            return True, summaries
            
        except Exception as e:
            return False, [{"error": f"Error getting conversations summary: {str(e)}"}]
    
    def get_agent_activity_summary(self, agent_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get activity summary for specific agent
        
        Returns:
            Tuple of (success: bool, activity_data: Dict)
        """
        try:
            # Get agent info
            agent_info = self.state_manager.get_agent_info(agent_id)
            if not agent_info:
                return False, {"error": f"Agent {agent_id} not found"}
            
            # Get all conversations
            conversations = self.state_manager.get_all_conversations()
            
            activity = {
                "agent_id": agent_id,
                "agent_name": agent_info.get("name"),
                "agent_type": agent_info.get("type"),
                "status": agent_info.get("status"),
                "last_active": agent_info.get("last_active"),
                "total_conversations": 0,
                "total_messages_sent": 0,
                "total_messages_received": 0,
                "pending_messages": 0,
                "active_conversations": []
            }
            
            # Analyze conversations
            for conv_id, conv_data in conversations.items():
                participants = conv_data.get("participants", [])
                
                if agent_id in participants:
                    activity["total_conversations"] += 1
                    
                    messages = conv_data.get("messages", [])
                    sent_count = sum(1 for msg in messages if msg.get("from") == agent_id)
                    received_count = sum(1 for msg in messages if msg.get("to") == agent_id)
                    pending_count = sum(1 for msg in messages if msg.get("to") == agent_id and msg.get("status") == "pending")
                    
                    activity["total_messages_sent"] += sent_count
                    activity["total_messages_received"] += received_count
                    activity["pending_messages"] += pending_count
                    
                    # Add to active conversations if has recent activity
                    if messages:  # Has messages
                        other_participant = [p for p in participants if p != agent_id][0] if len(participants) == 2 else "Unknown"
                        activity["active_conversations"].append({
                            "conversation_id": conv_id,
                            "with_agent": other_participant,
                            "last_update": conv_data.get("last_update"),
                            "message_count": len(messages),
                            "pending_for_me": pending_count
                        })
            
            # Sort active conversations by last update
            activity["active_conversations"].sort(key=lambda x: x.get("last_update", ""), reverse=True)
            
            return True, activity
            
        except Exception as e:
            return False, {"error": f"Error getting agent activity: {str(e)}"}
    
    def cleanup_old_conversations(self, days_old: int = 30) -> Tuple[bool, str]:
        """
        Clean up conversations older than specified days
        
        Returns:
            Tuple of (success: bool, result_message: str)
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            conversations = self.state_manager.get_all_conversations()
            
            conversations_to_delete = []
            
            for conv_id, conv_data in conversations.items():
                last_update_str = conv_data.get("last_update")
                if last_update_str:
                    try:
                        last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
                        if last_update < cutoff_date:
                            conversations_to_delete.append(conv_id)
                    except ValueError:
                        # Skip if date parsing fails
                        continue
            
            # Note: Actual deletion would require additional StateManager method
            # For now, just return info about what would be deleted
            
            if conversations_to_delete:
                return True, f"Found {len(conversations_to_delete)} conversations older than {days_old} days that could be cleaned up: {', '.join(conversations_to_delete)}"
            else:
                return True, f"No conversations found older than {days_old} days."
                
        except Exception as e:
            return False, f"Error during cleanup: {str(e)}"
    
    def export_conversation(self, conv_id: str, format_type: str = "text") -> Tuple[bool, str]:
        """
        Export conversation in specified format
        
        Returns:
            Tuple of (success: bool, exported_content: str)
        """
        try:
            conversation = self.state_manager.get_conversation(conv_id)
            if not conversation:
                return False, f"Conversation {conv_id} not found"
            
            if format_type == "text":
                return self._export_as_text(conversation)
            elif format_type == "json":
                return self._export_as_json(conversation)
            else:
                return False, f"Unsupported format: {format_type}"
                
        except Exception as e:
            return False, f"Error exporting conversation: {str(e)}"
    
    def _export_as_text(self, conversation: Dict[str, Any]) -> Tuple[bool, str]:
        """Export conversation as readable text"""
        lines = []
        
        # Header
        participants = conversation.get("participants", [])
        created_at = conversation.get("created_at", "Unknown")
        lines.append(f"Conversation between: {' and '.join(participants)}")
        lines.append(f"Created: {created_at}")
        lines.append("=" * 50)
        lines.append("")
        
        # Messages
        messages = conversation.get("messages", [])
        for msg in messages:
            from_agent = msg.get("from", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "Unknown")
            status = msg.get("status", "unknown")
            
            lines.append(f"[{timestamp}] {from_agent} ({status}):")
            lines.append(f"  {content}")
            lines.append("")
        
        return True, "\n".join(lines)
    
    def _export_as_json(self, conversation: Dict[str, Any]) -> Tuple[bool, str]:
        """Export conversation as JSON"""
        import json
        try:
            formatted_json = json.dumps(conversation, indent=2, ensure_ascii=False)
            return True, formatted_json
        except Exception as e:
            return False, f"Error formatting JSON: {str(e)}" 