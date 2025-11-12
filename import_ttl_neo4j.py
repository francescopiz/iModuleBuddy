import requests
import os


class GraphDBTTLLoader:
    """
    Automatically loads TTL files into GraphDB repository.

    Usage:
        loader = GraphDBTTLLoader()
    """

    def __init__(self,
                 graphdb_url="http://localhost:7200",
                 repository_id="IModuleBuddy",
                 ttl_file="ModuleSelection.ttl",
                 username=None,
                 password=None,
                 auto_load=True):
        """
        Initialize and auto-load TTL file into GraphDB.

        Args:
            graphdb_url: GraphDB server URL
            repository_id: Repository ID (default: "IModuleBuddy")
            ttl_file: Path to the TTL file
            username: Optional username for authentication
            password: Optional password for authentication
            auto_load: If True, automatically load on initialization
        """
        self.graphdb_url = graphdb_url.rstrip('/')
        self.repository_id = repository_id
        self.ttl_file = ttl_file
        self.username = username
        self.password = password

        self.statements_url = f"{self.graphdb_url}/repositories/{self.repository_id}/statements"

        # Validate TTL file exists
        if not os.path.exists(ttl_file):
            raise FileNotFoundError(f"TTL file not found: {ttl_file}")

        # Auto-load if enabled
        if auto_load:
            self.load_ttl()

    def _get_auth(self):
        """Get authentication tuple if credentials provided."""
        if self.username and self.password:
            return self.username, self.password
        return None

    def load_ttl(self):
        """Load TTL file directly into GraphDB repository."""
        try:
            print(f"Loading TTL file: {self.ttl_file}")
            print(f"Target repository: {self.repository_id}")

            # Read the TTL file
            with open(self.ttl_file, 'rb') as f:
                ttl_data = f.read()

            # Upload to GraphDB
            headers = {
                'Content-Type': 'application/x-turtle'
            }

            response = requests.post(
                self.statements_url,
                data=ttl_data,
                headers=headers,
                auth=self._get_auth()
            )

            if response.status_code in [200, 204]:
                print(f"✓ Successfully loaded {self.ttl_file} into repository '{self.repository_id}'")
            else:
                raise Exception(f"GraphDB returned status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"✗ Error loading TTL file: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    loader = GraphDBTTLLoader()