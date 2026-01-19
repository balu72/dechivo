#!/usr/bin/env python3
"""
Bulk loader for loading turtle files into Apache Jena Fuseki

This script loads all occupations, skills, and related data from the four frameworks
(CA, ESCO, O*NET, Singapore) into separate Fuseki datasets.
"""

from SPARQLWrapper import SPARQLWrapper, POST, BASIC, JSON
from rdflib import Graph, Namespace
from pathlib import Path
import sys
import time
import requests
from requests.auth import HTTPBasicAuth


class FusekiLoader:
    def __init__(self, fuseki_url="http://localhost:3030", username="admin", password="admin123"):
        self.fuseki_url = fuseki_url
        self.auth = HTTPBasicAuth(username, password)
        self.username = username
        self.password = password
        
    def dataset_exists(self, dataset_name):
        """Check if a dataset exists"""
        try:
            response = requests.get(
                f"{self.fuseki_url}/$/datasets",
                auth=self.auth
            )
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', [])
                return any(d.get('ds.name') == f"/{dataset_name}" for d in datasets)
            return False
        except Exception as e:
            print(f"  ⚠ Error checking dataset existence: {e}")
            return False
    
    def create_dataset(self, dataset_name, dataset_type="tdb2"):
        """Create a new dataset in Fuseki"""
        if self.dataset_exists(dataset_name):
            print(f"  ℹ Dataset '{dataset_name}' already exists, skipping creation")
            return True
        
        try:
            response = requests.post(
                f"{self.fuseki_url}/$/datasets",
                auth=self.auth,
                data={
                    "dbName": dataset_name,
                    "dbType": dataset_type
                }
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✓ Created dataset: {dataset_name}")
                return True
            else:
                print(f"  ✗ Failed to create dataset: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"  ✗ Error creating dataset: {e}")
            return False
    
    def load_turtle_file(self, dataset_name, file_path, graph_name=None):
        """Load a single turtle file into a dataset"""
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                ttl_content = f.read()
            
            # Determine the endpoint URL
            if graph_name:
                url = f"{self.fuseki_url}/{dataset_name}/data?graph={graph_name}"
            else:
                url = f"{self.fuseki_url}/{dataset_name}/data"
            
            # Upload the data
            response = requests.post(
                url,
                auth=self.auth,
                data=ttl_content.encode('utf-8'),
                headers={'Content-Type': 'text/turtle; charset=utf-8'}
            )
            
            if response.status_code in [200, 201, 204]:
                return True
            else:
                print(f"    ✗ Failed to load {file_path.name}: {response.status_code}")
                return False
        except Exception as e:
            print(f"    ✗ Error loading {file_path.name}: {e}")
            return False
    
    def load_directory(self, dataset_name, directory_path, graph_prefix=None):
        """Load all turtle files from a directory"""
        directory = Path(directory_path)
        ttl_files = list(directory.glob('*.ttl'))
        
        if not ttl_files:
            print(f"  ⚠ No turtle files found in {directory}")
            return 0
        
        print(f"  Loading {len(ttl_files)} files from {directory.name}...")
        
        loaded = 0
        failed = 0
        
        for i, ttl_file in enumerate(ttl_files, 1):
            # Create graph name if prefix provided
            graph_name = None
            if graph_prefix:
                # Use filename (without .ttl) as part of graph name
                file_id = ttl_file.stem
                graph_name = f"{graph_prefix}/{file_id}"
            
            if self.load_turtle_file(dataset_name, ttl_file, graph_name):
                loaded += 1
            else:
                failed += 1
            
            # Progress indicator
            if i % 100 == 0:
                print(f"    Progress: {i}/{len(ttl_files)} ({loaded} loaded, {failed} failed)")
        
        print(f"  ✓ Completed: {loaded} loaded, {failed} failed")
        return loaded
    
    def count_triples(self, dataset_name):
        """Count total triples in a dataset"""
        try:
            sparql = SPARQLWrapper(f"{self.fuseki_url}/{dataset_name}/query")
            sparql.setQuery("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
            sparql.setReturnFormat(JSON)
            sparql.setHTTPAuth(BASIC)
            sparql.setCredentials(self.username, self.password)
            
            results = sparql.query().convert()
            count = int(results["results"]["bindings"][0]["count"]["value"])
            return count
        except Exception as e:
            print(f"  ⚠ Error counting triples: {e}")
            return None
    
    def clear_dataset(self, dataset_name):
        """Clear all data from a dataset"""
        try:
            response = requests.post(
                f"{self.fuseki_url}/{dataset_name}/update",
                auth=self.auth,
                data="DROP ALL",
                headers={'Content-Type': 'application/sparql-update'}
            )
            
            if response.status_code in [200, 201, 204]:
                print(f"  ✓ Cleared dataset: {dataset_name}")
                return True
            else:
                print(f"  ✗ Failed to clear dataset: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Error clearing dataset: {e}")
            return False


def main():
    print("=" * 80)
    print("KNOWLEDGE GRAPH BULK LOADER")
    print("=" * 80)
    print()
    
    # Get data directory
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = Path(__file__).parent.parent.parent / 'data'
    
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Initialize loader
    loader = FusekiLoader()
    
    # Define datasets to create
    datasets = {
        'dechivo': 'Unified Dechivo Knowledge Graph',
        'ca': 'Canada OASIS Data',
        'esco': 'ESCO European Skills Data',
        'onet': 'O*NET US Occupation Data',
        'sg': 'Singapore SkillsFuture Data'
    }
    
    print("📦 Creating Datasets")
    print("-" * 80)
    for dataset_name, description in datasets.items():
        print(f"Creating {dataset_name}: {description}")
        loader.create_dataset(dataset_name)
    print()
    
    # Load data from each framework
    print("📥 Loading Data")
    print("-" * 80)
    
    frameworks = [
        ('ca', 'ca_turtle', 'http://dechivo.com/graph/ca'),
        ('esco', 'esco_turtle', 'http://dechivo.com/graph/esco'),
        ('onet', 'onet_turtle', 'http://dechivo.com/graph/onet'),
        ('sg', 'sg_turtle', 'http://dechivo.com/graph/sg'),
    ]
    
    total_loaded = 0
    
    for dataset_name, dir_name, graph_prefix in frameworks:
        framework_dir = data_dir / dir_name
        
        if not framework_dir.exists():
            print(f"⚠ Skipping {dataset_name}: directory not found")
            continue
        
        print(f"\n{dataset_name.upper()}: Loading from {dir_name}")
        print("-" * 80)
        
        # Load into framework-specific dataset
        loaded = loader.load_directory(dataset_name, framework_dir)
        total_loaded += loaded
        
        # Also load into unified 'dechivo' dataset with graph prefix
        print(f"  Loading into unified 'dechivo' dataset...")
        loader.load_directory('dechivo', framework_dir, graph_prefix)
        
        # Count triples
        count = loader.count_triples(dataset_name)
        if count is not None:
            print(f"  ℹ Total triples in '{dataset_name}': {count:,}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files loaded: {total_loaded}")
    print()
    
    # Count total triples in unified dataset
    print("Counting triples in unified dataset...")
    dechivo_count = loader.count_triples('dechivo')
    if dechivo_count is not None:
        print(f"✓ Total triples in 'dechivo': {dechivo_count:,}")
    print()
    
    print("✅ Data loading complete!")
    print()
    print("Next steps:")
    print("  1. Access Fuseki UI: http://localhost:3030")
    print("  2. Query datasets:")
    print("     - http://localhost:3030/dechivo/query (unified)")
    print("     - http://localhost:3030/ca/query")
    print("     - http://localhost:3030/esco/query")
    print("     - http://localhost:3030/onet/query")
    print("     - http://localhost:3030/sg/query")
    print()


if __name__ == '__main__':
    main()
