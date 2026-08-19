from datetime import datetime
from typing import Dict, Any, Optional
import json

from app.schemas.event import EventCreate
from app.services.validation import EventValidator


class EventNormalizer:
    """Normalizes source-specific telemetry into Sentinel's common event model."""
    
    @staticmethod
    def normalize_event(event_data: Dict[str, Any], source: Optional[str] = None) -> EventCreate:
        """
        Normalize event data into Sentinel's standard event model.
        
        Args:
            event_data: Raw event data from source
            source: Event source (e.g., 'ssh', 'windows_logs', 'syslog')
            
        Returns:
            Normalized EventCreate object
        """
        # Use the provided source or extract from event data
        event_source = source or event_data.get('source', 'unknown')
        
        # Normalize timestamp
        timestamp = EventValidator.validate_timestamp(event_data.get('timestamp'))
        
        # Build normalized event
        normalized = {
            'event_type': EventNormalizer._normalize_event_type(event_data, event_source),
            'source': event_source,
            'timestamp': timestamp,
            'host': EventNormalizer._normalize_host(event_data),
            'user': EventNormalizer._normalize_user(event_data),
            'normalized_data': EventNormalizer._extract_normalized_data(event_data, event_source),
            'raw_data': EventNormalizer._preserve_raw_data(event_data)
        }
        
        # Create EventCreate object
        return EventCreate(**normalized)
    
    @staticmethod
    def _normalize_event_type(event_data: Dict[str, Any], source: str) -> str:
        """Normalize event type based on source and content."""
        # If event_type is already provided, use it
        if 'event_type' in event_data and event_data['event_type']:
            return str(event_data['event_type'])[:100]  # Ensure max length
        
        # Derive event type from source and content
        event_type = 'unknown'
        
        # Source-specific normalization
        if source == 'ssh':
            if 'login' in str(event_data).lower() or 'auth' in str(event_data).lower():
                event_type = 'ssh_login'
            elif 'logout' in str(event_data).lower():
                event_type = 'ssh_logout'
            elif 'command' in str(event_data).lower():
                event_type = 'ssh_command'
        
        elif source == 'windows_logs':
            if 'login' in str(event_data).lower():
                event_type = 'windows_login'
            elif 'process' in str(event_data).lower():
                event_type = 'process_creation'
            elif 'network' in str(event_data).lower():
                event_type = 'network_connection'
        
        elif source == 'syslog':
            if 'error' in str(event_data).lower():
                event_type = 'system_error'
            elif 'warning' in str(event_data).lower():
                event_type = 'system_warning'
            else:
                event_type = 'system_event'
        
        return event_type[:100]  # Ensure max length
    
    @staticmethod
    def _normalize_host(event_data: Dict[str, Any]) -> Optional[str]:
        """Normalize hostname from event data."""
        # Try common host field names
        host_fields = ['host', 'hostname', 'computer', 'machine', 'server']
        for field in host_fields:
            if field in event_data and event_data[field]:
                return str(event_data[field])[:255]  # Ensure max length
        return None
    
    @staticmethod
    def _normalize_user(event_data: Dict[str, Any]) -> Optional[str]:
        """Normalize username from event data."""
        # Try common user field names
        user_fields = ['user', 'username', 'account', 'actor', 'principal']
        for field in user_fields:
            if field in event_data and event_data[field]:
                return str(event_data[field])[:255]  # Ensure max length
        return None
    
    @staticmethod
    def _extract_normalized_data(event_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Extract and normalize structured data from event."""
        normalized = {}
        
        # Extract source-specific fields
        if source == 'ssh':
            normalized = EventNormalizer._normalize_ssh_event(event_data)
        elif source == 'windows_logs':
            normalized = EventNormalizer._normalize_windows_event(event_data)
        elif source == 'syslog':
            normalized = EventNormalizer._normalize_syslog_event(event_data)
        else:
            # Generic normalization
            normalized = EventNormalizer._normalize_generic_event(event_data)
        
        return normalized
    
    @staticmethod
    def _normalize_ssh_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SSH-specific event data."""
        normalized = {}
        
        # SSH-specific fields
        if 'ip_address' in event_data:
            normalized['ip_address'] = event_data['ip_address']
        if 'port' in event_data:
            normalized['port'] = event_data['port']
        if 'protocol' in event_data:
            normalized['protocol'] = event_data['protocol']
        if 'auth_method' in event_data:
            normalized['auth_method'] = event_data['auth_method']
        
        return normalized
    
    @staticmethod
    def _normalize_windows_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Windows-specific event data."""
        normalized = {}
        
        # Windows-specific fields
        if 'event_id' in event_data:
            normalized['windows_event_id'] = event_data['event_id']
        if 'process_id' in event_data:
            normalized['process_id'] = event_data['process_id']
        if 'process_name' in event_data:
            normalized['process_name'] = event_data['process_name']
        if 'logon_type' in event_data:
            normalized['logon_type'] = event_data['logon_type']
        
        return normalized
    
    @staticmethod
    def _normalize_syslog_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize syslog-specific event data."""
        normalized = {}
        
        # Syslog-specific fields
        if 'priority' in event_data:
            normalized['priority'] = event_data['priority']
        if 'facility' in event_data:
            normalized['facility'] = event_data['facility']
        if 'program' in event_data:
            normalized['program'] = event_data['program']
        if 'pid' in event_data:
            normalized['pid'] = event_data['pid']
        
        return normalized
    
    @staticmethod
    def _normalize_generic_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize generic event data."""
        # Preserve all non-standard fields as-is
        normalized = {}
        
        # Skip already processed fields
        skip_fields = {'event_type', 'source', 'timestamp', 'host', 'user', 'raw_data'}
        
        for key, value in event_data.items():
            if key not in skip_fields and value is not None:
                normalized[key] = value
        
        return normalized
    
    @staticmethod
    def _preserve_raw_data(event_data: Dict[str, Any]) -> Optional[str]:
        """
        Preserve original event data as JSON string.
        
        Per ADR-005, original event data should be preserved
        to enable traceability back to source.
        """
        try:
            return json.dumps(event_data, default=str)
        except (TypeError, ValueError):
            # If JSON serialization fails, return string representation
            return str(event_data)
