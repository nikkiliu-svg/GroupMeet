"""
CAS (Central Authentication Service) client for Penn SSO integration.
<<<<<<< HEAD
=======
Adapted from cas-flask-demo.
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
"""
import requests
import xml.etree.ElementTree as ET
import logging
<<<<<<< HEAD
from urllib.parse import urlencode
=======
from urllib.parse import urlparse, parse_qs, urlencode
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)


class CASClient:
    """Client for interacting with Penn CAS server."""
    
    def __init__(self, cas_server_root: str):
<<<<<<< HEAD
=======
        """
        Initialize CAS client.
        
        Args:
            cas_server_root: Base URL of CAS server (must end with '/')
        """
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
        if not cas_server_root.endswith('/'):
            cas_server_root += '/'
        self.cas_server_root = cas_server_root
        self.service_validate_url = f"{cas_server_root}p3/serviceValidate.php"
    
    def get_login_url(self, service_url: str) -> str:
<<<<<<< HEAD
        """Generate CAS login URL with service parameter."""
        login_url = f"{self.cas_server_root}login.php"
        return f"{login_url}?{urlencode({'service': service_url})}"
    
    def get_logout_url(self, service_url: Optional[str] = None) -> str:
        """Generate CAS logout URL."""
        logout_url = f"{self.cas_server_root}logout.php"
        if service_url:
            return f"{logout_url}?{urlencode({'service': service_url})}"
=======
        """
        Get CAS login URL with service parameter.
        
        Args:
            service_url: URL to redirect back to after authentication
            
        Returns:
            Full CAS login URL
        """
        login_url = f"{self.cas_server_root}login.php"
        params = {'service': service_url}
        return f"{login_url}?{urlencode(params)}"
    
    def get_logout_url(self, service_url: Optional[str] = None) -> str:
        """
        Get CAS logout URL.
        
        Args:
            service_url: Optional URL to redirect to after logout
            
        Returns:
            CAS logout URL
        """
        logout_url = f"{self.cas_server_root}logout.php"
        if service_url:
            params = {'service': service_url}
            return f"{logout_url}?{urlencode(params)}"
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
        return logout_url
    
    def validate_ticket(self, ticket: str, service_url: str) -> Tuple[str, Dict]:
        """
<<<<<<< HEAD
        Validate CAS ticket and return PennKey and attributes.
        
        Args:
            ticket: CAS ticket from callback
            service_url: Service URL used in login
            
        Returns:
            Tuple of (pennkey, attributes_dict)
=======
        Validate CAS ticket and extract user information.
        
        Args:
            ticket: CAS service ticket
            service_url: Original service URL that generated the ticket
            
        Returns:
            Tuple of (pennkey, attributes_dict)
            
        Raises:
            Exception: If ticket validation fails
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
        """
        params = {
            'ticket': ticket,
            'service': service_url,
            'format': 'XML'
        }
<<<<<<< HEAD

        try:
            response = requests.get(self.service_validate_url, params=params, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            auth_success = root.find('.//{http://www.yale.edu/tp/cas}authenticationSuccess')

            if auth_success is None:
                auth_failure = root.find('.//{http://www.yale.edu/tp/cas}authenticationFailure')
                if auth_failure is not None:
                    code = auth_failure.get('code', 'UNKNOWN')
                    msg = auth_failure.text or 'Authentication failed'
                    raise Exception(f"CAS authentication failed: {code} - {msg}")
                raise Exception("Invalid CAS response: no authentication result found")

            user_element = auth_success.find('.//{http://www.yale.edu/tp/cas}user')
            if user_element is None or not user_element.text:
                raise Exception("No username found in CAS response")

            pennkey = user_element.text.strip()
            attributes = {}

            attr_el = auth_success.find('.//{http://www.yale.edu/tp/cas}attributes')
            if attr_el:
                for attr in attr_el:
                    tag = attr.tag.split('}')[-1]
                    attributes[tag] = attr.text

            logger.info(f"Successfully validated CAS ticket for user: {pennkey}")
            return pennkey, attributes

        except Exception as e:
            logger.error(f"Error validating CAS ticket: {e}")
            raise


def init_cas_client(app, server_root: str):
    """Initialize CAS client and attach to Flask app."""
    cas_client = CASClient(server_root)
    app.cas_client = cas_client
=======
        
        try:
            response = requests.get(self.service_validate_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Check for authentication success
            authentication_success = root.find('.//{http://www.yale.edu/tp/cas}authenticationSuccess')
            
            if authentication_success is None:
                # Check for authentication failure
                authentication_failure = root.find('.//{http://www.yale.edu/tp/cas}authenticationFailure')
                if authentication_failure is not None:
                    code = authentication_failure.get('code', 'UNKNOWN')
                    message = authentication_failure.text or 'Authentication failed'
                    logger.error(f"CAS authentication failed: {code} - {message}")
                    raise Exception(f"CAS authentication failed: {code} - {message}")
                else:
                    raise Exception("Invalid CAS response: no authentication result found")
            
            # Extract PennKey (username)
            user_element = authentication_success.find('.//{http://www.yale.edu/tp/cas}user')
            if user_element is None:
                user_element = root.find('.//{http://www.yale.edu/tp/cas}user')
            
            if user_element is None or user_element.text is None:
                raise Exception("No username found in CAS response")
            
            pennkey = user_element.text.strip()
            
            # Extract attributes
            attributes = {}
            attributes_element = authentication_success.find('.//{http://www.yale.edu/tp/cas}attributes')
            
            if attributes_element is not None:
                # Extract common attributes
                for attr in attributes_element:
                    # Remove namespace prefix
                    tag = attr.tag.split('}')[-1] if '}' in attr.tag else attr.tag
                    attributes[tag] = attr.text
            
            logger.info(f"Successfully validated CAS ticket for user: {pennkey}")
            return pennkey, attributes
            
        except requests.RequestException as e:
            logger.error(f"Error validating CAS ticket: {e}")
            raise Exception(f"Failed to validate CAS ticket: {str(e)}")
        except ET.ParseError as e:
            logger.error(f"Error parsing CAS XML response: {e}")
            raise Exception(f"Invalid CAS response format: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during CAS validation: {e}")
            raise


# Global CAS client instance (will be initialized in app factory)
cas_client = None


def init_cas_client(cas_server_root: str):
    """Initialize global CAS client."""
    global cas_client
    cas_client = CASClient(cas_server_root)
>>>>>>> 67c215ad34d18e611ecc954d4472e6c51138f8cd
    return cas_client

