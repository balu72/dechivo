#!/usr/bin/env python3
"""
Comprehensive TTL Merger Script

This script merges all 7,929 TTL files from 4 frameworks into a single
unified knowledge graph with entity resolution and provenance tracking.
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
from rdflib.namespace import DCTERMS, XSD, SKOS
from pathlib import Path
from collections import defaultdict
import json
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define namespaces
DV = Namespace('http://dechivo.com/ontology/')
DV_OCC = Namespace('http://dechivo.com/occupation/')
DV_SKILL = Namespace('http://dechivo.com/skill/')
ESCO = Namespace('http://data.europa.eu/esco/')
ONET = Namespace('http://data.onetcenter.org/')
SG = Namespace('http://data.skillsframework.sg/')
CA = Namespace('http://data.canada.ca/')


class TTLMerger:
    """Merges TTL files from multiple frameworks into unified knowledge graph"""
    
    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize main graph
        self.graph = Graph()
        
        # Bind namespaces
        self.graph.bind('dv', DV)
        self.graph.bind('dv-occ', DV_OCC)
        self.graph.bind('dv-skill', DV_SKILL)
        self.graph.bind('esco', ESCO)
        self.graph.bind('onet', ONET)
        self.graph.bind('sg', SG)
        self.graph.bind('ca', CA)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('owl', OWL)
        self.graph.bind('skos', SKOS)
        
        # Statistics
        self.stats = {
            'files_loaded': 0,
            'files_failed': 0,
            'triples_total': 0,
            'triples_by_framework': defaultdict(int),
            'entities_by_type': defaultdict(int)
        }
        
        # Framework configurations
        self.frameworks = {
            'ca': {'dir': 'ca_turtle', 'namespace': CA, 'name': 'Canada OASIS'},
            'esco': {'dir': 'esco_turtle', 'namespace': ESCO, 'name': 'ESCO'},
            'onet': {'dir': 'onet_turtle', 'namespace': ONET, 'name': 'O*NET'},
            'sg': {'dir': 'sg_turtle', 'namespace': SG, 'name': 'Singapore'}
        }
    
    def add_ontology_header(self):
        """Add ontology metadata and definitions"""
        logger.info("Adding ontology header...")
        
        # Ontology metadata
        dv_ontology = URIRef('http://dechivo.com/ontology')
        self.graph.add((dv_ontology, RDF.type, OWL.Ontology))
        self.graph.add((dv_ontology, RDFS.label, Literal("Dechivo Unified Ontology")))
        self.graph.add((dv_ontology, DCTERMS.description, 
                       Literal("Unified knowledge graph integrating occupation and skills data from ESCO, O*NET, Singapore SkillsFuture, and Canada OASIS")))
        self.graph.add((dv_ontology, DCTERMS.created, 
                       Literal(datetime.now().date(), datatype=XSD.date)))
        self.graph.add((dv_ontology, OWL.versionInfo, Literal("1.0")))
        
        # Define core classes
        classes = [
            (DV.Occupation, "Occupation or job role"),
            (DV.Skill, "Skill or competency"),
            (DV.Knowledge, "Knowledge area"),
            (DV.Ability, "Ability or aptitude"),
            (DV.Technology, "Technology or tool"),
            (DV.Competency, "Competency framework element"),
            (DV.Sector, "Industry sector")
        ]
        
        for class_uri, description in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(class_uri.split('/')[-1])))
            self.graph.add((class_uri, DCTERMS.description, Literal(description)))
        
        # Define core properties
        properties = [
            (DV.requiresSkill, "Requires skill"),
            (DV.requiresKnowledge, "Requires knowledge"),
            (DV.requiresAbility, "Requires ability"),
            (DV.requiresCompetency, "Requires competency"),
            (DV.usesTechnology, "Uses technology"),
            (DV.hasEssentialSkill, "Has essential skill"),
            (DV.hasOptionalSkill, "Has optional skill"),
            (DV.belongsToSector, "Belongs to sector"),
            (DV.fromFramework, "Source framework"),
            (DV.proficiencyLevel, "Proficiency level"),
            (DV.medianSalary, "Median salary"),
            (DV.jobOutlook, "Job outlook")
        ]
        
        for prop_uri, description in properties:
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(prop_uri.split('/')[-1])))
            self.graph.add((prop_uri, DCTERMS.description, Literal(description)))
        
        logger.info("✓ Ontology header added")
    
    def load_framework_files(self, framework_key: str):
        """Load all TTL files from a specific framework"""
        framework = self.frameworks[framework_key]
        framework_dir = self.data_dir / framework['dir']
        
        if not framework_dir.exists():
            logger.warning(f"Directory not found: {framework_dir}")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Loading {framework['name']} ({framework_key.upper()})")
        logger.info(f"{'='*80}")
        
        ttl_files = list(framework_dir.glob('*.ttl'))
        total_files = len(ttl_files)
        
        logger.info(f"Found {total_files} TTL files")
        
        loaded = 0
        failed = 0
        triples_before = len(self.graph)
        
        for i, ttl_file in enumerate(ttl_files, 1):
            try:
                # Parse and merge
                temp_graph = Graph()
                temp_graph.parse(str(ttl_file), format='turtle')
                
                # Add all triples to main graph
                for triple in temp_graph:
                    self.graph.add(triple)
                
                # Add provenance for each subject
                for subj in temp_graph.subjects(unique=True):
                    if isinstance(subj, URIRef):
                        self.graph.add((subj, DV.fromFramework, 
                                      Literal(framework['name'])))
                
                loaded += 1
                
                # Progress update every 100 files
                if i % 100 == 0 or i == total_files:
                    logger.info(f"  Progress: {i}/{total_files} files ({loaded} loaded, {failed} failed)")
                
            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Failed to load {ttl_file.name}: {e}")
        
        triples_added = len(self.graph) - triples_before
        
        logger.info(f"\n✓ {framework['name']} complete:")
        logger.info(f"  - Files loaded: {loaded}/{total_files}")
        logger.info(f"  - Files failed: {failed}")
        logger.info(f"  - Triples added: {triples_added:,}")
        
        # Update statistics
        self.stats['files_loaded'] += loaded
        self.stats['files_failed'] += failed
        self.stats['triples_by_framework'][framework_key] = triples_added
    
    def add_entity_mappings(self):
        """Add entity resolution mappings if available"""
        logger.info("\n" + "="*80)
        logger.info("Adding Entity Mappings")
        logger.info("="*80)
        
        mapping_file = Path(__file__).parent.parent / 'occupation_mappings.ttl'
        
        if mapping_file.exists():
            logger.info(f"Loading mappings from {mapping_file.name}...")
            try:
                self.graph.parse(str(mapping_file), format='turtle')
                logger.info("✓ Entity mappings added")
            except Exception as e:
                logger.warning(f"⚠ Failed to load entity mappings: {e}")
        else:
            logger.info("ℹ No entity mapping file found (occupation_mappings.ttl)")
            logger.info("  Run map_entities.py first to generate mappings")
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics about the merged graph"""
        logger.info("\n" + "="*80)
        logger.info("Calculating Statistics")
        logger.info("="*80)
        
        self.stats['triples_total'] = len(self.graph)
        
        # Count by type
        type_counts = defaultdict(int)
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            if isinstance(o, URIRef):
                type_name = str(o).split('/')[-1]
                type_counts[type_name] += 1
        
        self.stats['entities_by_type'] = dict(type_counts)
        
        logger.info(f"\nTotal triples: {self.stats['triples_total']:,}")
        logger.info(f"\nTriples by framework:")
        for framework, count in self.stats['triples_by_framework'].items():
            logger.info(f"  - {framework.upper()}: {count:,}")
        
        logger.info(f"\nEntities by type:")
        for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  - {entity_type}: {count:,}")
    
    def save_graph(self, filename: str):
        """Serialize graph to TTL file"""
        logger.info("\n" + "="*80)
        logger.info("Saving Unified Knowledge Graph")
        logger.info("="*80)
        
        output_file = self.output_dir / filename
        
        logger.info(f"Serializing to {output_file}...")
        logger.info(f"Total triples: {len(self.graph):,}")
        
        try:
            self.graph.serialize(destination=str(output_file), format='turtle')
            
            # Get file size
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            
            logger.info(f"✓ File saved successfully!")
            logger.info(f"  - Path: {output_file}")
            logger.info(f"  - Size: {file_size_mb:.2f} MB")
            logger.info(f"  - Triples: {len(self.graph):,}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"✗ Failed to save graph: {e}")
            raise
    
    def save_statistics(self):
        """Save statistics to JSON file"""
        stats_file = self.output_dir / 'merge_statistics.json'
        
        stats_output = {
            'merge_date': datetime.now().isoformat(),
            'total_files_loaded': self.stats['files_loaded'],
            'total_files_failed': self.stats['files_failed'],
            'total_triples': self.stats['triples_total'],
            'triples_by_framework': dict(self.stats['triples_by_framework']),
            'entities_by_type': dict(self.stats['entities_by_type'])
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_output, f, indent=2)
        
        logger.info(f"\n✓ Statistics saved to {stats_file}")
    
    def run(self):
        """Execute the complete merging process"""
        logger.info("="*80)
        logger.info("DECHIVO KNOWLEDGE GRAPH MERGER")
        logger.info("="*80)
        logger.info(f"\nData directory: {self.data_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Add ontology header
        self.add_ontology_header()
        
        # Step 2: Load all frameworks
        for framework_key in ['ca', 'esco', 'onet', 'sg']:
            self.load_framework_files(framework_key)
        
        # Step 3: Add entity mappings
        self.add_entity_mappings()
        
        # Step 4: Calculate statistics
        self.calculate_statistics()
        
        # Step 5: Save unified graph
        output_file = self.save_graph('unified_knowledge_graph.ttl')
        
        # Step 6: Save statistics
        self.save_statistics()
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("MERGE COMPLETE!")
        logger.info("="*80)
        logger.info(f"\n✅ Successfully created unified knowledge graph!")
        logger.info(f"\nSummary:")
        logger.info(f"  - Files processed: {self.stats['files_loaded']}")
        logger.info(f"  - Files failed: {self.stats['files_failed']}")
        logger.info(f"  - Total triples: {self.stats['triples_total']:,}")
        logger.info(f"  - Output file: {output_file}")
        logger.info(f"\nFramework contributions:")
        for fw, count in self.stats['triples_by_framework'].items():
            logger.info(f"  - {fw.upper()}: {count:,} triples")
        logger.info(f"\nNext steps:")
        logger.info(f"  1. Review merge_statistics.json")
        logger.info(f"  2. Load unified_knowledge_graph.ttl into Fuseki")
        logger.info(f"  3. Test queries on unified dataset")
        logger.info(f"\n✨ Done!")


def main():
    """Main entry point"""
    print("="*80)
    print("TTL MERGER - Dechivo Knowledge Graph")
    print("="*80)
    print()
    
    # Get directories
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = Path(__file__).parent.parent.parent / 'data'
    
    output_dir = data_dir / 'unified-files'
    
    # Validate data directory
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        print(f"  Please provide a valid data directory path")
        print(f"  Usage: python3 merge_ttl.py /path/to/data")
        sys.exit(1)
    
    # Create merger
    merger = TTLMerger(data_dir, output_dir)
    
    # Run merge process
    try:
        merger.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Merge failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
