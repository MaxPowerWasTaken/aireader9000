# tests/health_check.py
import sys
from typing import Optional

import requests


def check_site_health(url: str, connect_timeout: int = 10, read_timeout: int = 30) -> Optional[str]:
    """
    Check if a site is healthy by making a GET request.
    
    Args:
        url: The URL to check
        connect_timeout: Timeout for establishing connection (seconds)
        read_timeout: Timeout for completing the request (seconds)
        
    Returns:
        None if site is healthy, error message string if not
    """
    try:
        response = requests.get(
            url, 
            timeout=(connect_timeout, read_timeout)
        )
        response.raise_for_status()
        return None
    except requests.ConnectionError:
        return f"Failed to connect to {url}"
    except requests.Timeout:
        return f"Timeout connecting to {url}"
    except requests.RequestException as e:
        return f"Error checking {url}: {str(e)}"

def main() -> int:
    """Run health check and return exit code (0 for success, 1 for failure)."""
    url = "https://aireader9000.streamlit.app/"
    error = check_site_health(url)
    
    if error:
        print(error, file=sys.stderr)
        return 1
    
    print(f"Successfully connected to {url}")
    return 0

if __name__ == "__main__":
    sys.exit(main())