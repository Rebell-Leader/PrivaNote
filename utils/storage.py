import streamlit as st
import json
from datetime import datetime

class StorageService:
    """Handle local storage of meeting data using Streamlit session state"""
    
    def __init__(self):
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage in session state"""
        if 'meetings' not in st.session_state:
            st.session_state.meetings = []
        if 'storage_version' not in st.session_state:
            st.session_state.storage_version = "1.0"
    
    def save_meeting(self, meeting_data):
        """
        Save meeting data to local storage
        
        Args:
            meeting_data (dict): Complete meeting data
            
        Returns:
            str: Meeting ID
        """
        try:
            # Ensure meeting has required fields
            if not all(key in meeting_data for key in ['title', 'transcript', 'analysis']):
                raise ValueError("Meeting data missing required fields")
            
            # Add metadata
            meeting_data['saved_at'] = datetime.now().isoformat()
            meeting_data['version'] = "1.0"
            
            # Add to session state
            st.session_state.meetings.append(meeting_data)
            
            return meeting_data['id']
            
        except Exception as e:
            raise Exception(f"Failed to save meeting: {str(e)}")
    
    def get_meeting(self, meeting_id):
        """
        Retrieve specific meeting by ID
        
        Args:
            meeting_id (str): Meeting ID
            
        Returns:
            dict or None: Meeting data or None if not found
        """
        for meeting in st.session_state.meetings:
            if meeting.get('id') == meeting_id:
                return meeting
        return None
    
    def get_all_meetings(self):
        """
        Get all stored meetings
        
        Returns:
            list: List of all meeting data
        """
        return st.session_state.meetings.copy()
    
    def update_meeting(self, meeting_id, updated_data):
        """
        Update existing meeting data
        
        Args:
            meeting_id (str): Meeting ID
            updated_data (dict): Updated meeting data
            
        Returns:
            bool: True if updated, False if not found
        """
        for i, meeting in enumerate(st.session_state.meetings):
            if meeting.get('id') == meeting_id:
                # Preserve original creation time
                updated_data['created_at'] = meeting.get('created_at')
                updated_data['updated_at'] = datetime.now().isoformat()
                st.session_state.meetings[i] = updated_data
                return True
        return False
    
    def delete_meeting(self, meeting_id):
        """
        Delete meeting by ID
        
        Args:
            meeting_id (str): Meeting ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, meeting in enumerate(st.session_state.meetings):
            if meeting.get('id') == meeting_id:
                del st.session_state.meetings[i]
                return True
        return False
    
    def clear_all_meetings(self):
        """Clear all stored meetings"""
        st.session_state.meetings = []
    
    def search_meetings(self, query, fields=None):
        """
        Search meetings by text query
        
        Args:
            query (str): Search query
            fields (list, optional): Fields to search in
            
        Returns:
            list: Matching meetings
        """
        if fields is None:
            fields = ['title', 'transcript', 'notes']
        
        query_lower = query.lower()
        matching_meetings = []
        
        for meeting in st.session_state.meetings:
            # Search in specified fields
            search_text = ""
            for field in fields:
                if field in meeting:
                    if isinstance(meeting[field], str):
                        search_text += " " + meeting[field]
                    elif isinstance(meeting[field], dict):
                        # Search in analysis fields
                        if field == 'analysis':
                            search_text += " " + meeting[field].get('summary', '')
                            search_text += " " + " ".join(meeting[field].get('action_items', []))
                            search_text += " " + " ".join(meeting[field].get('key_decisions', []))
            
            if query_lower in search_text.lower():
                matching_meetings.append(meeting)
        
        return matching_meetings
    
    def get_storage_stats(self):
        """
        Get storage statistics
        
        Returns:
            dict: Storage statistics
        """
        meetings = st.session_state.meetings
        
        if not meetings:
            return {
                'total_meetings': 0,
                'total_duration': 0,
                'storage_size_estimate': 0,
                'oldest_meeting': None,
                'newest_meeting': None
            }
        
        total_duration = sum(meeting.get('duration', 0) for meeting in meetings)
        
        # Estimate storage size (rough calculation)
        total_text = 0
        for meeting in meetings:
            total_text += len(meeting.get('transcript', ''))
            total_text += len(str(meeting.get('analysis', {})))
        
        storage_size_mb = (total_text * 2) / (1024 * 1024)  # Rough estimate
        
        # Find date range
        dates = [meeting.get('created_at') for meeting in meetings if meeting.get('created_at')]
        oldest = min(dates) if dates else None
        newest = max(dates) if dates else None
        
        return {
            'total_meetings': len(meetings),
            'total_duration': total_duration,
            'storage_size_estimate': storage_size_mb,
            'oldest_meeting': oldest,
            'newest_meeting': newest
        }
    
    def export_all_data(self):
        """
        Export all meeting data as JSON
        
        Returns:
            str: JSON string of all data
        """
        export_data = {
            'export_date': datetime.now().isoformat(),
            'version': st.session_state.get('storage_version', '1.0'),
            'meetings': st.session_state.meetings
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_data(self, json_data):
        """
        Import meeting data from JSON
        
        Args:
            json_data (str): JSON string containing meeting data
            
        Returns:
            int: Number of meetings imported
        """
        try:
            data = json.loads(json_data)
            imported_meetings = data.get('meetings', [])
            
            # Validate imported data
            valid_meetings = []
            for meeting in imported_meetings:
                if all(key in meeting for key in ['title', 'transcript', 'analysis']):
                    valid_meetings.append(meeting)
            
            # Add to existing meetings (avoid duplicates by ID)
            existing_ids = {m.get('id') for m in st.session_state.meetings}
            new_meetings = [m for m in valid_meetings if m.get('id') not in existing_ids]
            
            st.session_state.meetings.extend(new_meetings)
            
            return len(new_meetings)
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")
