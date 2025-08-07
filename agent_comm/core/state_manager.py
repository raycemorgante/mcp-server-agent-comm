"""
State Manager - Handles JSON file operations for shared state
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterable

from ..constants import (
    CONVERSATIONS_FILE,
    PENDING_CALLS_FILE, 
    AGENT_REGISTRY_FILE,
    MESSAGE_STATUS
)


class StateManager:
    """Manages shared state via JSON files"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        # Initialize conversations.json
        if not CONVERSATIONS_FILE.exists():
            self._write_json(CONVERSATIONS_FILE, {})
        
        # Initialize pending_calls.json
        if not PENDING_CALLS_FILE.exists():
            self._write_json(PENDING_CALLS_FILE, {})
        
        # Initialize agent_registry.json
        if not AGENT_REGISTRY_FILE.exists():
            self._write_json(AGENT_REGISTRY_FILE, {})
    
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
    
    def register_agent(self, agent_id: str, agent_name: str, agent_type: str = "custom"):
        """Register a new agent"""
        registry = self._read_json(AGENT_REGISTRY_FILE)
        registry[agent_id] = {
            "name": agent_name,
            "type": agent_type,
            "registered_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "status": "online"
        }
        self._write_json(AGENT_REGISTRY_FILE, registry)
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        registry = self._read_json(AGENT_REGISTRY_FILE)
        return registry.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents"""
        return self._read_json(AGENT_REGISTRY_FILE)
    
    def update_agent_activity(self, agent_id: str):
        """Update agent's last activity time"""
        registry = self._read_json(AGENT_REGISTRY_FILE)
        if agent_id in registry:
            registry[agent_id]["last_active"] = datetime.now().isoformat()
            registry[agent_id]["status"] = "online"
            self._write_json(AGENT_REGISTRY_FILE, registry)
    
    def add_pending_call(self, agent_id: str, message: str = None):
        """Add a pending tool call"""
        pending = self._read_json(PENDING_CALLS_FILE)
        pending[agent_id] = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "waiting": True
        }
        self._write_json(PENDING_CALLS_FILE, pending)
    
    def remove_pending_call(self, agent_id: str):
        """Remove pending tool call"""
        pending = self._read_json(PENDING_CALLS_FILE)
        if agent_id in pending:
            del pending[agent_id]
            self._write_json(PENDING_CALLS_FILE, pending)
    
    def get_pending_calls(self) -> Dict[str, Any]:
        """Get all pending calls"""
        return self._read_json(PENDING_CALLS_FILE)
    
    def create_conversation(self, participants: List[str]) -> str:
        """Create new conversation between agents"""
        conv_id = f"{'_'.join(sorted(participants))}_{int(time.time())}"
        conversations = self._read_json(CONVERSATIONS_FILE)

        conversations[conv_id] = {
            "participants": list(participants),
            "created_at": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "message_count": 0,
            "messages": []
        }

        self._write_json(CONVERSATIONS_FILE, conversations)
        return conv_id

    def add_message(self, conv_id: str, from_agent: str, message: str) -> str:
        """Add message to conversation and broadcast to all participants"""
        conversations = self._read_json(CONVERSATIONS_FILE)

        if conv_id not in conversations:
            raise ValueError(f"Conversation {conv_id} not found")

        participants = conversations[conv_id]["participants"]
        recipients = [p for p in participants if p != from_agent]

        msg_id = f"msg_{len(conversations[conv_id]['messages']) + 1}"
        new_message = {
            "id": msg_id,
            "from": from_agent,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "status": {recipient: MESSAGE_STATUS["PENDING"] for recipient in recipients}
        }

        conversations[conv_id]["messages"].append(new_message)
        conversations[conv_id]["message_count"] += 1
        conversations[conv_id]["last_update"] = datetime.now().isoformat()

        self._write_json(CONVERSATIONS_FILE, conversations)
        return msg_id
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation"""
        conversations = self._read_json(CONVERSATIONS_FILE)
        return conversations.get(conv_id)
    
    def get_all_conversations(self) -> Dict[str, Any]:
        """Get all conversations"""
        return self._read_json(CONVERSATIONS_FILE)
    
    def get_pending_messages_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all pending messages for specific agent"""
        conversations = self._read_json(CONVERSATIONS_FILE)
        pending_messages = []

        for conv_id, conv_data in conversations.items():
            for message in conv_data["messages"]:
                status = message.get("status", {})
                if status.get(agent_id) == MESSAGE_STATUS["PENDING"]:
                    pending_messages.append({
                        "conversation_id": conv_id,
                        "message": message
                    })

        return pending_messages
    
    def mark_message_delivered(self, conv_id: str, message_id: str, agent_id: str):
        """Mark message as delivered for a specific agent"""
        conversations = self._read_json(CONVERSATIONS_FILE)

        if conv_id in conversations:
            for message in conversations[conv_id]["messages"]:
                if message["id"] == message_id:
                    if agent_id in message.get("status", {}):
                        message["status"][agent_id] = MESSAGE_STATUS["DELIVERED"]
                    break

            self._write_json(CONVERSATIONS_FILE, conversations)

    def find_conversation(self, participants: Iterable[str]) -> Optional[str]:
        """Find existing conversation by participant set"""
        participant_set = set(participants)
        conversations = self._read_json(CONVERSATIONS_FILE)

        for conv_id, conv_data in conversations.items():
            if set(conv_data.get("participants", [])) == participant_set:
                return conv_id

        return None