import os
import uuid
from datetime import datetime
from typing import List, Dict

class SessionManager:
    def __init__(self):
        # In-memory storage for MVP
        # session_id -> { "files": [FileMetadata], "last_activity": datetime }
        self.sessions: Dict[str, Dict] = {}

    def get_or_create_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "files": [],
                "last_activity": datetime.now()
            }
        else:
            self.sessions[session_id]["last_activity"] = datetime.now()
        return self.sessions[session_id]

    def add_file(self, session_id: str, file_meta: Dict):
        session = self.get_or_create_session(session_id)
        session["files"].append(file_meta)

    def get_files(self, session_id: str) -> List[Dict]:
        session = self.get_or_create_session(session_id)
        return session["files"]

    def remove_file(self, session_id: str, file_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["files"] = [
                f for f in self.sessions[session_id]["files"] if f["id"] != file_id
            ]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
