"""
Database abstraction layer for GroupMeet.
Supports Firebase Firestore and Google Sheets with easy swapping.
"""
import json
import uuid
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    def save_submission(self, data: Dict[str, Any]) -> str:
        """Save a submission and return its ID."""
        pass
    
    @abstractmethod
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get a submission by ID."""
        pass
    
    @abstractmethod
    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all submissions."""
        pass
    
    @abstractmethod
    def save_match(self, match_data: Dict[str, Any]) -> str:
        """Save a match result and return its ID."""
        pass
    
    @abstractmethod
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get a match by ID."""
        pass
    
    @abstractmethod
    def get_matches_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all matches for a student."""
        pass


class FirestoreDB(DatabaseInterface):
    """Firebase Firestore implementation."""
    
    def __init__(self, project_id: str, credentials_path: str):
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:
                if credentials_path:
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            self.project_id = project_id
            logger.info("Firestore database initialized")
        except ImportError:
            raise ImportError("firebase-admin not installed. Run: pip3 install firebase-admin")
        except Exception as e:
            logger.warning(f"Firestore initialization failed: {e}. Using in-memory fallback.")
            raise
    
    def save_submission(self, data: Dict[str, Any]) -> str:
        """Save submission to Firestore."""
        from firebase_admin import firestore
        submission_id = str(uuid.uuid4())
        data['id'] = submission_id
        data['created_at'] = firestore.SERVER_TIMESTAMP
        self.db.collection('submissions').document(submission_id).set(data)
        return submission_id
    
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission from Firestore."""
        doc = self.db.collection('submissions').document(submission_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all submissions from Firestore."""
        docs = self.db.collection('submissions').stream()
        return [doc.to_dict() for doc in docs]
    
    def save_match(self, match_data: Dict[str, Any]) -> str:
        """Save match to Firestore."""
        from firebase_admin import firestore
        match_id = str(uuid.uuid4())
        match_data['id'] = match_id
        match_data['created_at'] = firestore.SERVER_TIMESTAMP
        self.db.collection('matches').document(match_id).set(match_data)
        return match_id
    
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match from Firestore."""
        doc = self.db.collection('matches').document(match_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_matches_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """Get matches for a student."""
        matches = self.db.collection('matches').where('student_ids', 'array_contains', student_id).stream()
        return [doc.to_dict() for doc in matches]


class SheetsDB(DatabaseInterface):
    """Google Sheets implementation."""
    
    def __init__(self, sheet_id: str, credentials_path: str):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(sheet_id)
            self.submissions_sheet = self.sheet.worksheet('Submissions')
            self.matches_sheet = self.sheet.worksheet('Matches')
            logger.info("Google Sheets database initialized")
        except ImportError:
            raise ImportError("gspread not installed. Run: pip3 install gspread")
        except Exception as e:
            logger.warning(f"Sheets initialization failed: {e}")
            raise
    
    def save_submission(self, data: Dict[str, Any]) -> str:
        """Save submission to Sheets."""
        submission_id = str(uuid.uuid4())
        data['id'] = submission_id
        row = [
            submission_id,
            data.get('name', ''),
            data.get('email', ''),
            data.get('course', ''),
            json.dumps(data.get('availability', [])),
            data.get('study_preference', ''),
            json.dumps(data)
        ]
        self.submissions_sheet.append_row(row)
        return submission_id
    
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission from Sheets."""
        records = self.submissions_sheet.get_all_records()
        for record in records:
            if record.get('id') == submission_id:
                return json.loads(record.get('data', '{}'))
        return None
    
    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all submissions from Sheets."""
        records = self.submissions_sheet.get_all_records()
        return [json.loads(record.get('data', '{}')) for record in records]
    
    def save_match(self, match_data: Dict[str, Any]) -> str:
        """Save match to Sheets."""
        match_id = str(uuid.uuid4())
        match_data['id'] = match_id
        row = [
            match_id,
            json.dumps(match_data.get('student_ids', [])),
            json.dumps(match_data.get('group_members', [])),
            json.dumps(match_data)
        ]
        self.matches_sheet.append_row(row)
        return match_id
    
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match from Sheets."""
        records = self.matches_sheet.get_all_records()
        for record in records:
            if record.get('id') == match_id:
                return json.loads(record.get('data', '{}'))
        return None
    
    def get_matches_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """Get matches for a student."""
        records = self.matches_sheet.get_all_records()
        matches = []
        for record in records:
            student_ids = json.loads(record.get('student_ids', '[]'))
            if student_id in student_ids:
                matches.append(json.loads(record.get('data', '{}')))
        return matches


class InMemoryDB(DatabaseInterface):
    """In-memory database for development/testing."""
    
    def __init__(self):
        self.submissions: Dict[str, Dict[str, Any]] = {}
        self.matches: Dict[str, Dict[str, Any]] = {}
        logger.info("In-memory database initialized (development mode)")
    
    def save_submission(self, data: Dict[str, Any]) -> str:
        """Save submission to memory."""
        submission_id = str(uuid.uuid4())
        data['id'] = submission_id
        self.submissions[submission_id] = data
        return submission_id
    
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission from memory."""
        return self.submissions.get(submission_id)
    
    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all submissions from memory."""
        return list(self.submissions.values())
    
    def save_match(self, match_data: Dict[str, Any]) -> str:
        """Save match to memory."""
        match_id = str(uuid.uuid4())
        match_data['id'] = match_id
        self.matches[match_id] = match_data
        return match_id
    
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match from memory."""
        return self.matches.get(match_id)
    
    def get_matches_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """Get matches for a student."""
        return [
            match for match in self.matches.values()
            if student_id in match.get('student_ids', [])
        ]


def get_database(config) -> DatabaseInterface:
    """
    Factory function to get the appropriate database instance.
    
    Args:
        config: Configuration object
        
    Returns:
        DatabaseInterface instance
    """
    db_type = config.DB_TYPE.lower()
    
    if db_type == 'firestore':
        try:
            return FirestoreDB(
                config.FIREBASE_PROJECT_ID,
                config.FIREBASE_CREDENTIALS_PATH
            )
        except Exception as e:
            logger.warning(f"Firestore init failed: {e}. Falling back to in-memory.")
            return InMemoryDB()
    
    elif db_type == 'sheets':
        try:
            return SheetsDB(
                config.GOOGLE_SHEETS_ID,
                config.GOOGLE_CREDENTIALS_PATH
            )
        except Exception as e:
            logger.warning(f"Sheets init failed: {e}. Falling back to in-memory.")
            return InMemoryDB()
    
    else:
        logger.info("Using in-memory database (default)")
        return InMemoryDB()

