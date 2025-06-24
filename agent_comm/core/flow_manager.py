"""
Flow Manager - Handles workflow between Agent Chat tools and Controller
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..constants import SHARED_DATA_DIR


class FlowManager:
    """Manages workflow between Agent Chat 1, Agent Chat 2, and Controller"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.waiting_agents_file = SHARED_DATA_DIR / "waiting_agents.json"
        self.message_queue_file = SHARED_DATA_DIR / "message_queue.json"
        self.conversation_flow_file = SHARED_DATA_DIR / "conversation_flow.json"
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        files_to_init = [
            (self.waiting_agents_file, {}),
            (self.message_queue_file, {"pending_messages": []}),
            (self.conversation_flow_file, {"active_conversations": []})
        ]
        
        for file_path, default_data in files_to_init:
            if not file_path.exists():
                self._write_json(file_path, default_data)
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """Safely read JSON file"""
        with self._lock:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]):
        """Safely write JSON file"""
        with self._lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_waiting_agent(self, agent_tool: str, agent_id: str, message: str = None) -> str:
        """
        Register an agent as waiting for response
        
        Args:
            agent_tool: "agent_chat_1" or "agent_chat_2"
            agent_id: ID of the agent (e.g., "claude_001")
            message: Message content (if sending)
        
        Returns:
            waiting_id: Unique ID for this waiting session
        """
        waiting_data = self._read_json(self.waiting_agents_file)
        
        waiting_id = f"{agent_tool}_{int(time.time())}"
        
        waiting_data[waiting_id] = {
            "agent_tool": agent_tool,
            "agent_id": agent_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "waiting"
        }
        
        self._write_json(self.waiting_agents_file, waiting_data)
        
        # Add to message queue if message provided
        if message:
            self.add_message_to_queue(agent_id, message, waiting_id)
        
        return waiting_id
    
    def add_message_to_queue(self, from_agent: str, message: str, waiting_id: str):
        """Add message to queue for delivery"""
        queue_data = self._read_json(self.message_queue_file)
        
        # Ensure queue data structure exists
        if "pending_messages" not in queue_data:
            queue_data["pending_messages"] = []
        
        # Ensure pending_messages is a list
        if not isinstance(queue_data["pending_messages"], list):
            queue_data["pending_messages"] = []
        
        message_entry = {
            "id": f"msg_{int(time.time())}",
            "from_agent": from_agent,
            "message": message,
            "waiting_id": waiting_id,
            "timestamp": datetime.now().isoformat(),
            "delivered": False
        }
        
        queue_data["pending_messages"].append(message_entry)
        
        self._write_json(self.message_queue_file, queue_data)
    
    def get_waiting_agents(self) -> Dict[str, Any]:
        """Get all agents currently waiting"""
        return self._read_json(self.waiting_agents_file)
    
    def get_message_queue(self) -> List[Dict[str, Any]]:
        """Get pending messages queue"""
        queue_data = self._read_json(self.message_queue_file)
        return queue_data.get("pending_messages", [])
    
    def deliver_message_to_agent(self, waiting_id: str, message_content: str) -> bool:
        """
        Deliver message to waiting agent
        
        Args:
            waiting_id: ID of waiting agent session
            message_content: Message to deliver
        
        Returns:
            True if successful
        """
        waiting_data = self._read_json(self.waiting_agents_file)
        
        if waiting_id in waiting_data:
            # Update status to delivered
            waiting_data[waiting_id]["status"] = "delivered"
            waiting_data[waiting_id]["delivered_message"] = message_content
            waiting_data[waiting_id]["delivered_at"] = datetime.now().isoformat()
            
            self._write_json(self.waiting_agents_file, waiting_data)
            return True
        
        return False
    
    def remove_waiting_agent(self, waiting_id: str):
        """Remove agent from waiting state"""
        waiting_data = self._read_json(self.waiting_agents_file)
        
        if waiting_id in waiting_data:
            del waiting_data[waiting_id]
            self._write_json(self.waiting_agents_file, waiting_data)
    
    def mark_message_delivered(self, message_id: str):
        """Mark message as delivered in queue"""
        queue_data = self._read_json(self.message_queue_file)
        
        for msg in queue_data["pending_messages"]:
            if msg["id"] == message_id:
                msg["delivered"] = True
                msg["delivered_at"] = datetime.now().isoformat()
                break
        
        self._write_json(self.message_queue_file, queue_data)
    
    def get_agent_status(self, waiting_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific waiting agent"""
        waiting_data = self._read_json(self.waiting_agents_file)
        return waiting_data.get(waiting_id)
    
    def wait_for_delivery(self, waiting_id: str, timeout: int = None) -> Optional[str]:
        """
        Wait for message delivery to this agent
        
        Args:
            waiting_id: ID of waiting session
            timeout: Maximum wait time in seconds (None for infinite wait)
        
        Returns:
            Delivered message content or None if timeout (never with infinite wait)
        """
        start_time = time.time()
        
        while True:
            status = self.get_agent_status(waiting_id)
            
            if status and status.get("status") == "delivered":
                return status.get("delivered_message")
            
            # Check timeout only if specified
            if timeout is not None and time.time() - start_time >= timeout:
                return None  # Timeout
            
            time.sleep(1)  # Check every second
    
    def get_controller_data(self) -> Dict[str, Any]:
        """Get all data needed for controller UI"""
        return {
            "waiting_agents": self.get_waiting_agents(),
            "message_queue": self.get_message_queue(),
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup_old_data(self, hours: int = 24):
        """Clean up old waiting agents and messages"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Clean waiting agents
        waiting_data = self._read_json(self.waiting_agents_file)
        cleaned_waiting = {}
        
        for waiting_id, data in waiting_data.items():
            timestamp_str = data.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp > cutoff_time:
                    cleaned_waiting[waiting_id] = data
            except ValueError:
                # Keep if can't parse timestamp
                cleaned_waiting[waiting_id] = data
        
        self._write_json(self.waiting_agents_file, cleaned_waiting)
        
        # Clean message queue
        queue_data = self._read_json(self.message_queue_file)
        cleaned_messages = []
        
        for msg in queue_data.get("pending_messages", []):
            timestamp_str = msg.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp > cutoff_time or not msg.get("delivered", False):
                    cleaned_messages.append(msg)
            except ValueError:
                cleaned_messages.append(msg)
        
        queue_data["pending_messages"] = cleaned_messages
        self._write_json(self.message_queue_file, queue_data)
    
    def delete_messages(self, message_ids: List[str]) -> int:
        """
        Delete specific messages from queue
        
        Args:
            message_ids: List of message IDs to delete
        
        Returns:
            Number of messages actually deleted
        """
        if not message_ids:
            return 0
        
        queue_data = self._read_json(self.message_queue_file)
        
        # Filter out messages with matching IDs
        original_count = len(queue_data.get("pending_messages", []))
        queue_data["pending_messages"] = [
            msg for msg in queue_data.get("pending_messages", [])
            if msg.get("id") not in message_ids
        ]
        
        new_count = len(queue_data["pending_messages"])
        deleted_count = original_count - new_count
        
        # Write back the updated queue
        self._write_json(self.message_queue_file, queue_data)
        
        return deleted_count
    
    def clear_all_data(self):
        """Clear ALL data - for complete reset"""
        # Reset all files to empty state
        self._write_json(self.waiting_agents_file, {})
        self._write_json(self.message_queue_file, {"pending_messages": []})
        self._write_json(self.conversation_flow_file, {"active_conversations": []}) 