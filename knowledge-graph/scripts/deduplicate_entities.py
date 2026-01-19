#!/usr/bin/env python3
"""
Entity Deduplication Script

This script removes duplicate occupations from the unified knowledge graph,
consolidating them into canonical entities with owl:sameAs references.
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
from rdflib.namespace import DCTERMS, XSD, SKOS
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Namespaces
DV = Namespace('http://dechivo.com/ontology/')
DV_OCC = Namespace('http://dechivo.com/occupation/')
ESCO = Namespace('http://data.europa.eu/esco/')
ONET = Namespace('http://data.onetcenter.org/')
SG = Namespace('http://data.skillsframework.sg/')
CA = Namespace('http://data.canada.ca/')


class EntityDeduplicator:
    """Removes duplicate entities and creates canonical references"""
    
    def __init__(self, input_file: Path, output_dir: Path):
        self.input_file = input_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load graph
        logger.info(f"Loading knowledge graph from {input_file}...")
        self.graph = Graph()
        self.graph.parse(str(input_file), format='turtle')
        logger.info(f"✓ Loaded {len(self.graph):,} triples")
        
        # Statistics
        self.stats = {
            'original_triples': len(self.graph),
            'occupations_found': 0,
            'duplicates_found': 0,
            'canonical_created': 0,
            'triples_removed': 0,
            'triples_added': 0
        }
        
        # Occupation mappings
        self.occupation_map = defaultdict(list)  # canonical_label -> [uris]
        self.frameworks = ['ESCO', 'O*NET', 'Singapore', 'Canada OASIS']
    
    def normalize_label(self, label: str) -> str:
        """Normalize occupation label for comparison"""
        normalized = label.lower().strip()
        
        # Remove common variations
        replacements = [
            (' and ', ' & '),
            (' / ', '/'),
            ('  ', ' '),
            (',', ''),
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def calculate_similarity(self, label1: str, label2: str) -> float:
        """Calculate similarity between two labels"""
        norm1 = self.normalize_label(label1)
        norm2 = self.normalize_label(label2)
        
        if norm1 == norm2:
            return 1.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_occupations(self):
        """Find all occupation entities in the graph"""
        logger.info("\n" + "="*80)
        logger.info("Finding Occupations")
        logger.info("="*80)
        
        occupation_types = [
            ESCO.Occupation,
            ONET.Occupation,
            SG.Occupation,
            URIRef('http://data.canada.ca/oasis/Occupation')
        ]
        
        occupations = {}
        
        for occ_type in occupation_types:
            for subj in self.graph.subjects(RDF.type, occ_type):
                label = self.graph.value(subj, RDFS.label)
                if label:
                    occupations[str(subj)] = {
                        'uri': str(subj),
                        'label': str(label),
                        'type': str(occ_type)
                    }
        
        logger.info(f"Found {len(occupations)} occupation entities")
        self.stats['occupations_found'] = len(occupations)
        
        return occupations
    
    def group_duplicates(self, occupations: dict) -> dict:
        """Group duplicate occupations by normalized label"""
        logger.info("\n" + "="*80)
        logger.info("Grouping Duplicates")
        logger.info("="*80)
        
        # Group by normalized label
        label_groups = defaultdict(list)
        
        for uri, occ_data in occupations.items():
            normalized = self.normalize_label(occ_data['label'])
            label_groups[normalized].append(occ_data)
        
        # Find groups with duplicates
        duplicates = {}
        unique_count = 0
        
        for norm_label, group in label_groups.items():
            if len(group) > 1:
                # This is a duplicate group
                canonical_label = group[0]['label']  # Use first as canonical
                duplicates[canonical_label] = group
            else:
                unique_count += 1
        
        logger.info(f"Duplicate groups found: {len(duplicates)}")
        logger.info(f"Unique occupations: {unique_count}")
        
        # Show sample duplicates
        logger.info("\nSample duplicate groups:")
        for i, (label, group) in enumerate(list(duplicates.items())[:10]):
            logger.info(f"  {i+1}. '{label}' ({len(group)} variants)")
            for occ in group:
                framework = 'Unknown'
                if 'europa.eu/esco' in occ['uri']:
                    framework = 'ESCO'
                elif 'onetcenter.org' in occ['uri']:
                    framework = 'O*NET'
                elif 'skillsframework.sg' in occ['uri']:
                    framework = 'Singapore'
                elif 'canada.ca' in occ['uri']:
                    framework = 'Canada'
                logger.info(f"     - {framework}: {occ['uri'][:60]}...")
        
        self.stats['duplicates_found'] = len(duplicates)
        return duplicates
    
    def create_canonical_entities(self, duplicates: dict):
        """Create canonical occupation entities with owl:sameAs references"""
        logger.info("\n" + "="*80)
        logger.info("Creating Canonical Entities")
        logger.info("="*80)
        
        triples_before = len(self.graph)
        
        for canonical_label, group in duplicates.items():
            # Create canonical URI
            canonical_id = self.normalize_label(canonical_label).replace(' ', '_').replace('/', '_')
            canonical_uri = DV_OCC[canonical_id]
            
            # Add canonical entity
            self.graph.add((canonical_uri, RDF.type, DV.Occupation))
            self.graph.add((canonical_uri, RDFS.label, Literal(canonical_label, lang='en')))
            
            # Collect all descriptions
            descriptions = []
            frameworks = []
            
            for occ in group:
                occ_uri = URIRef(occ['uri'])
                
                # Get description
                desc = self.graph.value(occ_uri, DCTERMS.description)
                if desc and str(desc) not in descriptions:
                    descriptions.append(str(desc))
                
                # Determine framework
                uri_str = occ['uri']
                if 'europa.eu/esco' in uri_str:
                    frameworks.append('ESCO')
                elif 'onetcenter.org' in uri_str:
                    frameworks.append('O*NET')
                elif 'skillsframework.sg' in uri_str:
                    frameworks.append('Singapore')
                elif 'canada.ca' in uri_str:
                    frameworks.append('Canada')
                
                # Add owl:sameAs
                self.graph.add((canonical_uri, OWL.sameAs, occ_uri))
            
            # Add combined description
            if descriptions:
                combined_desc = " | ".join(descriptions[:3])  # Use first 3 descriptions
                self.graph.add((canonical_uri, DCTERMS.description, Literal(combined_desc, lang='en')))
            
            # Add framework provenance
            for framework in set(frameworks):
                self.graph.add((canonical_uri, DV.fromFramework, Literal(framework)))
            
            # Add metadata
            self.graph.add((canonical_uri, DCTERMS.created, 
                          Literal(datetime.now().date(), datatype=XSD.date)))
            self.graph.add((canonical_uri, DV.hasVariants, Literal(len(group))))
        
        triples_added = len(self.graph) - triples_before
        
        logger.info(f"✓ Created {len(duplicates)} canonical entities")
        logger.info(f"  Triples added: {triples_added:,}")
        
        self.stats['canonical_created'] = len(duplicates)
        self.stats['triples_added'] = triples_added
    
    def remove_duplicate_relationships(self, duplicates: dict):
        """Remove relationships from duplicate entities (keep canonical only)"""
        logger.info("\n" + "="*80)
        logger.info("Removing Duplicate Relationships")
        logger.info("="*80)
        
        triples_before = len(self.graph)
        removed = 0
        
        # For each duplicate group
        for canonical_label, group in duplicates.items():
            # Get canonical URI
            canonical_id = self.normalize_label(canonical_label).replace(' ', '_').replace('/', '_')
            canonical_uri = DV_OCC[canonical_id]
            
            # Keep the first variant as source, remove others
            keep_uri = URIRef(group[0]['uri'])
            duplicate_uris = [URIRef(occ['uri']) for occ in group[1:]]
            
            # For each duplicate (except the one we're keeping)
            for dup_uri in duplicate_uris:
                # Remove all triples where this is the subject
                # (except the type and owl:sameAs relationships)
                for p, o in list(self.graph.predicate_objects(dup_uri)):
                    if p not in [RDF.type, OWL.sameAs, RDFS.label]:
                        self.graph.remove((dup_uri, p, o))
                        removed += 1
                
                # Remove all triples where this is the object
                for s, p in list(self.graph.subject_predicates(dup_uri)):
                    if p != OWL.sameAs:
                        self.graph.remove((s, p, dup_uri))
                        removed += 1
        
        logger.info(f"✓ Removed {removed:,} duplicate relationship triples")
        
        self.stats['triples_removed'] = removed
    
    def save_deduplicated_graph(self, filename: str):
        """Save the deduplicated graph"""
        logger.info("\n" + "="*80)
        logger.info("Saving Deduplicated Knowledge Graph")
        logger.info("="*80)
        
        output_file = self.output_dir / filename
        
        logger.info(f"Serializing to {output_file}...")
        logger.info(f"Total triples: {len(self.graph):,}")
        
        self.graph.serialize(destination=str(output_file), format='turtle')
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        
        logger.info(f"✓ File saved successfully!")
        logger.info(f"  - Path: {output_file}")
        logger.info(f"  - Size: {file_size_mb:.2f} MB")
        logger.info(f"  - Triples: {len(self.graph):,}")
        
        return output_file
    
    def save_statistics(self):
        """Save deduplication statistics"""
        stats_file = self.output_dir / 'deduplication_statistics.json'
        
        stats_output = {
            'deduplication_date': datetime.now().isoformat(),
            'original_triples': self.stats['original_triples'],
            'final_triples': len(self.graph),
            'triples_removed': self.stats['triples_removed'],
            'triples_added': self.stats['triples_added'],
            'occupations_found': self.stats['occupations_found'],
            'duplicate_groups': self.stats['duplicates_found'],
            'canonical_entities_created': self.stats['canonical_created'],
            'unique_occupations': self.stats['occupations_found'] - self.stats['duplicates_found']
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_output, f, indent=2)
        
        logger.info(f"\n✓ Statistics saved to {stats_file}")
    
    def run(self):
        """Execute the complete deduplication process"""
        logger.info("="*80)
        logger.info("ENTITY DEDUPLICATION")
        logger.info("="*80)
        logger.info(f"\nInput file: {self.input_file}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Find all occupations
        occupations = self.find_occupations()
        
        # Step 2: Group duplicates
        duplicates = self.group_duplicates(occupations)
        
        # Step 3: Create canonical entities
        self.create_canonical_entities(duplicates)
        
        # Step 4: Remove duplicate relationships
        self.remove_duplicate_relationships(duplicates)
        
        # Step 5: Save deduplicated graph
        output_file = self.save_deduplicated_graph('deduplicated_knowledge_graph.ttl')
        
        # Step 6: Save statistics
        self.save_statistics()
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("DEDUPLICATION COMPLETE!")
        logger.info("="*80)
        logger.info(f"\n✅ Successfully deduplicated knowledge graph!")
        logger.info(f"\nSummary:")
        logger.info(f"  - Original triples: {self.stats['original_triples']:,}")
        logger.info(f"  - Final triples: {len(self.graph):,}")
        logger.info(f"  - Net change: {len(self.graph) - self.stats['original_triples']:+,}")
        logger.info(f"  - Duplicate groups: {self.stats['duplicates_found']}")
        logger.info(f"  - Canonical entities created: {self.stats['canonical_created']}")
        logger.info(f"  - Output file: {output_file}")
        logger.info(f"\n✨ Done!")


def main():
    import sys
    
    print("="*80)
    print("ENTITY DEDUPLICATION - Dechivo Knowledge Graph")
    print("="*80)
    print()
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path(__file__).parent.parent.parent / 'data' / 'unified-files' / 'unified_knowledge_graph.ttl'
    
    if not input_file.exists():
        print(f"✗ Input file not found: {input_file}")
        print(f"  Usage: python3 deduplicate_entities.py /path/to/unified_kg.ttl")
        sys.exit(1)
    
    output_dir = input_file.parent
    
    # Create deduplicator
    dedup = EntityDeduplicator(input_file, output_dir)
    
    # Run deduplication
    try:
        dedup.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Deduplication failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
