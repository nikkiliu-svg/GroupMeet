"""
CAS (Central Authentication Service) client for Penn SSO integration.
"""
import requests
import xml.etree.ElementTree as ET
import logging
from urllib.parse import urlencode
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)


class CASClient:
    """Client for interacting with Penn CAS server."""
    
    def __init__(self, cas_server_root: str):
        if not cas_server_root.endswith('/'):
            cas_server_root += '/'
        self.cas_server_root = cas_server_root
        self.service_validate_url = f"{cas_server_root}p3/serviceValidate.php"
    
    def get_login_url(self, service_url: str) -> str:
        """Generate CAS login URL with service parameter."""
        login_url = f"{self.cas_server_root}login.php"
        return f"{login_url}?{urlencode({'service': service_url})}"
    
    def get_logout_url(self, service_url: Optional[str] = None) -> str:
        """Generate CAS logout URL."""
        logout_url = f"{self.cas_server_root}logout.php"
        if service_url:
            return f"{logout_url}?{urlencode({'service': service_url})}"
        return logout_url
    
    def validate_ticket(self, ticket: str, service_url: str) -> Tuple[str, Dict]:
        """
        Validate CAS ticket and return PennKey and attributes.
        
        Args:
            ticket: CAS ticket from callback
            service_url: Service URL used in login
            
        Returns:
            Tuple of (pennkey, attributes_dict)
        """
        params = {
            'ticket': ticket,
            'service': service_url,
            'format': 'XML'
        }

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
    return cas_client

