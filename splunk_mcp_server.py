from mcp.server.fastmcp import FastMCP
import requests
import time
import urllib3
import json

# Suppress insecure request warnings if using self-signed certs for Splunk
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize FastMCP Server
mcp = FastMCP("AgentShield-Splunk")

# Splunk Enterprise Credentials
SPLUNK_HOST = "https://localhost:8089"
USER = "ajith"
PASS = "ajith123"

@mcp.tool()
def search_splunk(query: str) -> str:
    """Execute a Splunk SPL search and return the results as JSON. Use this to investigate AI agent security incidents and logs."""
    
    # Ensure query starts with "search "
    if not query.strip().lower().startswith("search "):
        query = "search " + query
        
    auth = (USER, PASS)
    search_url = f"{SPLUNK_HOST}/services/search/jobs"
    
    # Splunk expects form-encoded data
    data = {
        "search": query,
        "output_mode": "json",
        "exec_mode": "normal"
    }
    
    try:
        # Start the search job
        response = requests.post(search_url, auth=auth, data=data, verify=False)
        response.raise_for_status()
        
        sid = response.json().get("sid")
        if not sid:
            return "Error: Could not retrieve Search ID (sid) from Splunk."
            
        # Poll for completion
        status_url = f"{search_url}/{sid}"
        is_done = False
        
        # Poll up to 15 times (15 seconds)
        for _ in range(15):
            status_res = requests.get(status_url, auth=auth, params={"output_mode": "json"}, verify=False)
            status_res.raise_for_status()
            content = status_res.json()
            
            # Check the dispatchState or isDone flag
            entry = content.get("entry", [{}])[0].get("content", {})
            if entry.get("isDone") or entry.get("dispatchState") == "DONE":
                is_done = True
                break
                
            time.sleep(1)
            
        if not is_done:
            return f"Error: Splunk search {sid} did not complete within the timeout period."
            
        # Retrieve results
        results_url = f"{status_url}/results"
        results_res = requests.get(results_url, auth=auth, params={"output_mode": "json"}, verify=False)
        results_res.raise_for_status()
        
        # Process and return the results
        results = results_res.json().get("results", [])
        return json.dumps(results, indent=2)
        
    except requests.exceptions.RequestException as e:
        return f"Splunk API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
