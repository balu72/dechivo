#!/usr/bin/env python3
"""
Fuseki Dataset Manager - Replace old datasets with unified KG

This script:
1. Removes old framework-specific datasets (ca, esco, onet, sg, dechivo)
2. Creates new 'unified' dataset
3. Loads deduplicated knowledge graph
"""

import requests
from requests.auth import HTTPBasicAuth
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FUSEKI_URL = "http://localhost:3030"
USERNAME = "admin"
PASSWORD = "admin123"

class FusekiManager:
    def __init__(self):
        self.base_url = FUSEKI_URL
        self.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    def delete_dataset(self, dataset_name: str):
        """Delete a Fuseki dataset"""
        url = f"{self.base_url}/$/datasets/{dataset_name}"
        
        try:
            response = requests.delete(url, auth=self.auth)
            if response.status_code in [200, 404]:
                if response.status_code == 404:
                    logger.info(f"  Dataset '{dataset_name}' doesn't exist (already deleted)")
                else:
                    logger.info(f"  ✓ Deleted dataset '{dataset_name}'")
                return True
            else:
                logger.error(f"  ✗ Failed to delete '{dataset_name}': {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"  ✗ Error deleting '{dataset_name}': {e}")
            return False
    
    def create_dataset(self, dataset_name: str):
        """Create a new Fuseki dataset"""
        url = f"{self.base_url}/$/datasets"
        
        data = {
            "dbName": dataset_name,
            "dbType": "tdb2"
        }
        
        try:
            response = requests.post(url, auth=self.auth, data=data)
            if response.status_code in [200, 409]:
                if response.status_code == 409:
                    logger.info(f"  Dataset '{dataset_name}' already exists")
                else:
                    logger.info(f"  ✓ Created dataset '{dataset_name}'")
                return True
            else:
                logger.error(f"  ✗ Failed to create '{dataset_name}': {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"  ✗ Error creating '{dataset_name}': {e}")
            return False
    
    def load_ttl_file(self, dataset_name: str, ttl_file: Path):
        """Load TTL file into dataset"""
        url = f"{self.base_url}/{dataset_name}/data"
        
        logger.info(f"  Loading {ttl_file.name} ({ttl_file.stat().st_size / 1024 / 1024:.2f} MB)...")
        
        try:
            with open(ttl_file, 'rb') as f:
                headers = {'Content-Type': 'text/turtle;charset=utf-8'}
                response = requests.post(url, auth=self.auth, headers=headers, data=f)
            
            if response.status_code in [200, 201]:
                logger.info(f"  ✓ Loaded successfully")
                return True
            else:
                logger.error(f"  ✗ Failed to load: {response.status_code}")
                logger.error(f"  Response: {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"  ✗ Error loading file: {e}")
            return False
    
    def count_triples(self, dataset_name: str):
        """Count triples in dataset"""
        url = f"{self.base_url}/{dataset_name}/query"
        
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        
        try:
            response = requests.post(
                url,
                auth=self.auth,
                headers={'Content-Type': 'application/sparql-query'},
                data=query
            )
            
            if response.status_code == 200:
                result = response.json()
                count = int(result['results']['bindings'][0]['count']['value'])
                logger.info(f"  ✓ Dataset '{dataset_name}' contains {count:,} triples")
                return count
            else:
                logger.error(f"  ✗ Failed to count triples: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"  ✗ Error counting triples: {e}")
            return None
    
    def list_datasets(self):
        """List all datasets"""
        url = f"{self.base_url}/$/datasets"
        
        try:
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                datasets = response.json()['datasets']
                return [d['ds.name'].lstrip('/') for d in datasets]
            else:
                logger.error(f"Failed to list datasets: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []


def main():
    print("="*80)
    print("FUSEKI DATASET REPLACEMENT")
    print("="*80)
    print()
    
    manager = FusekiManager()
    
    # Step 1: List current datasets
    logger.info("Step 1: Checking current datasets...")
    current_datasets = manager.list_datasets()
    logger.info(f"Found {len(current_datasets)} datasets: {', '.join(current_datasets)}")
    print()
    
    # Step 2: Delete old datasets
    logger.info("Step 2: Removing old framework-specific datasets...")
    old_datasets = ['ca', 'esco', 'onet', 'sg', 'dechivo']
    
    for dataset in old_datasets:
        if dataset in current_datasets:
            manager.delete_dataset(dataset)
        time.sleep(0.5)
    
    print()
    
    # Step 3: Create new unified dataset
    logger.info("Step 3: Creating unified dataset...")
    manager.create_dataset('unified')
    time.sleep(1)
    print()
    
    # Step 4: Load deduplicated knowledge graph
    logger.info("Step 4: Loading deduplicated knowledge graph...")
    
    ttl_file = Path(__file__).parent.parent.parent / 'data' / 'unified-files' / 'deduplicated_knowledge_graph.ttl'
    
    if not ttl_file.exists():
        logger.error(f"✗ File not found: {ttl_file}")
        return False
    
    success = manager.load_ttl_file('unified', ttl_file)
    
    if not success:
        logger.error("✗ Failed to load knowledge graph")
        return False
    
    print()
    
    # Step 5: Verify loading
    logger.info("Step 5: Verifying loaded data...")
    time.sleep(2)  # Give Fuseki time to index
    
    count = manager.count_triples('unified')
    
    if count and count > 1000000:
        logger.info(f"✅ SUCCESS! Loaded {count:,} triples")
    else:
        logger.warning(f"⚠️  Loaded {count:,} triples (expected ~1.7M)")
    
    print()
    
    # Step 6: List final datasets
    logger.info("Step 6: Final dataset list...")
    final_datasets = manager.list_datasets()
    logger.info(f"Active datasets: {', '.join(final_datasets)}")
    
    print()
    print("="*80)
    print("REPLACEMENT COMPLETE!")
    print("="*80)
    print()
    print("✅ Old datasets removed:")
    for ds in old_datasets:
        print(f"   - {ds}")
    print()
    print("✅ New dataset created:")
    print(f"   - unified (1.73M triples)")
    print()
    print("Next steps:")
    print("  1. Update API endpoints to use 'unified' dataset")
    print("  2. Restart backend: cd backend && python3 app.py")
    print("  3. Test queries: curl http://localhost:5000/api/kg/health")
    print()
    
    return True


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
