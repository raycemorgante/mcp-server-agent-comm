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
    
    def register_waiting_agent(
        self,
        agent_tool: str,
        agent_id: str,
        message: str = None,
        participants: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        skip_queue: bool = False,
    ) -> str:
        """Register an agent as waiting and associate with a conversation"""
        waiting_data = self._read_json(self.waiting_agents_file)

        if participants is None:
            participants = [agent_id]

        if conversation_id is None:
            conversation_id = f"conv_{int(time.time())}"

        # Update conversation tracking
        conv_data = self._read_json(self.conversation_flow_file)
        conv_list = conv_data.get("active_conversations", [])
        existing = next((c for c in conv_list if c.get("conversation_id") == conversation_id), None)
        if existing:
            existing_participants = set(existing.get("participants", []))
            existing_participants.update(participants)
            existing["participants"] = list(existing_participants)
            existing["last_update"] = datetime.now().isoformat()
        else:
            conv_list.append(
                {
                    "conversation_id": conversation_id,
                    "participants": list(participants),
                    "created_at": datetime.now().isoformat(),
                    "last_update": datetime.now().isoformat(),
                }
            )
        conv_data["active_conversations"] = conv_list
        self._write_json(self.conversation_flow_file, conv_data)

        waiting_id = f"{agent_tool}_{int(time.time())}"

        waiting_data[waiting_id] = {
            "agent_tool": agent_tool,
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "participants": list(participants),
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "waiting",
        }

        self._write_json(self.waiting_agents_file, waiting_data)

        if message and not skip_queue:
            self.add_message_to_queue(conversation_id, agent_id, message, participants, waiting_id)

        return waiting_id

    def add_message_to_queue(
        self,
        conversation_id: str,
        from_agent: str,
        message: str,
        participants: List[str],
        waiting_id: Optional[str] = None,
    ):
        """Add message to queue for delivery within a conversation"""
        queue_data = self._read_json(self.message_queue_file)

        if "pending_messages" not in queue_data or not isinstance(
            queue_data.get("pending_messages"), list
        ):
            queue_data["pending_messages"] = []

        targets = [p for p in participants if p != from_agent]
        message_entry = {
            "id": f"msg_{int(time.time())}",
            "conversation_id": conversation_id,
            "from_agent": from_agent,
            "message": message,
            "targets": targets,
            "timestamp": datetime.now().isoformat(),
            "delivered": {t: False for t in targets},
        }
        if waiting_id:
            message_entry["waiting_id"] = waiting_id

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
    
    def mark_message_delivered(self, message_id: str, agent_ids: Optional[List[str]] = None):
        """Mark message as delivered for specified agents"""
        queue_data = self._read_json(self.message_queue_file)

        for msg in queue_data.get("pending_messages", []):
            if msg.get("id") == message_id:
                delivered = msg.setdefault("delivered", {})
                if agent_ids is None:
                    agent_ids = list(delivered.keys())
                for agent in agent_ids:
                    if agent in delivered:
                        delivered[agent] = True
                msg["delivered_all"] = all(delivered.values()) if delivered else True
                if msg["delivered_all"]:
                    msg["delivered_at"] = datetime.now().isoformat()
                break

        self._write_json(self.message_queue_file, queue_data)

    def deliver_message_to_participants(
        self,
        conversation_id: str,
        agent_ids: List[str],
        message_content: str,
        message_id: str,
    ) -> bool:
        """Deliver message content to specified participants"""
        waiting_data = self._read_json(self.waiting_agents_file)
        delivered_any = False

        for waiting_id, agent_data in waiting_data.items():
            if (
                agent_data.get("conversation_id") == conversation_id
                and agent_data.get("agent_id") in agent_ids
                and agent_data.get("status") == "waiting"
            ):
                agent_data["status"] = "delivered"
                agent_data["delivered_message"] = message_content
                agent_data["delivered_at"] = datetime.now().isoformat()
                delivered_any = True

        if delivered_any:
            self._write_json(self.waiting_agents_file, waiting_data)
            self.mark_message_delivered(message_id, agent_ids)

        return delivered_any
    
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
    
    def get_conversations(self) -> Dict[str, Any]:
        """Return active conversations with participant lists"""
        conv_data = self._read_json(self.conversation_flow_file)
        conversations = {}
        for conv in conv_data.get("active_conversations", []):
            conv_id = conv.get("conversation_id")
            if conv_id:
                conversations[conv_id] = conv
        return conversations

    def get_controller_data(self) -> Dict[str, Any]:
        """Get all data needed for controller UI"""
        return {
            "conversations": self.get_conversations(),
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