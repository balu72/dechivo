#!/usr/bin/env python3
"""
Entity Mapping and Resolution Script

This script identifies and maps equivalent entities (occupations) across
the four frameworks (CA, ESCO, O*NET, Singapore).
"""

from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.namespace import SKOS, DCTERMS
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import json
from difflib import SequenceMatcher
import sys


# Namespaces
DV = Namespace('http://dechivo.com/ontology/')
DV_OCC = Namespace('http://dechivo.com/occupation/')


class EntityMapper:
    """Map equivalent entities across frameworks"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.occupations = {
            'ca': {},
            'esco': {},
            'onet': {},
            'sg': {}
        }
        self.mappings = defaultdict(lambda: defaultdict(list))
        
    def load_occupations(self):
        """Load all occupations from turtle files"""
        print("Loading occupations from all frameworks...")
        
        frameworks = {
            'ca': ('ca_turtle', 'http://data.canada.ca/occupation/'),
            'esco': ('esco_turtle', 'http://data.europa.eu/esco/occupation/'),
            'onet': ('onet_turtle', 'http://data.onetcenter.org/occupation/'),
            'sg': ('sg_turtle', 'http://data.skillsframework.sg/occupation/')
        }
        
        for framework, (dir_name, namespace) in frameworks.items():
            framework_dir = self.data_dir / dir_name
            if not framework_dir.exists():
                print(f"  ⚠ {framework.upper()}: directory not found")
                continue
            
            ttl_files = list(framework_dir.glob('*.ttl'))
            occ_count = 0
            
            for ttl_file in ttl_files:
                try:
                    g = Graph()
                    g.parse(str(ttl_file), format='turtle')
                    
                    # Extract occupations
                    for subj in g.subjects(RDF.type, None):
                        if namespace in str(subj):
                            label = g.value(subj, RDFS.label)
                            if label:
                                description = g.value(subj, DCTERMS.description)
                                alt_labels = list(g.objects(subj, SKOS.altLabel))
                                
                                self.occupations[framework][str(subj)] = {
                                    'uri': str(subj),
                                    'label': str(label),
                                    'description': str(description) if description else '',
                                    'alt_labels': [str(al) for al in alt_labels],
                                    'source_file': ttl_file.name
                                }
                                occ_count += 1
                except Exception as e:
                    continue
            
            print(f"  ✓ {framework.upper()}: loaded {occ_count} occupations")
    
    def normalize_label(self, label: str) -> str:
        """Normalize occupation label for comparison"""
        # Convert to lowercase, remove extra spaces, common variations
        normalized = label.lower().strip()
        
        # Remove common suffixes/prefixes
        replacements = [
            (' and ', ' & '),
            (' / ', '/'),
            ('  ', ' '),
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def calculate_similarity(self, label1: str, label2: str) -> float:
        """Calculate similarity score between two labels (0-1)"""
        norm1 = self.normalize_label(label1)
        norm2 = self.normalize_label(label2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_exact_matches(self):
        """Find exact label matches across frameworks"""
        print("\nFinding exact matches...")
        
        # Build index by normalized labels
        label_index = defaultdict(list)
        
        for framework, occupations in self.occupations.items():
            for uri, occ_data in occupations.items():
                normalized = self.normalize_label(occ_data['label'])
                label_index[normalized].append((framework, uri, occ_data))
                
                # Also index alternative labels
                for alt_label in occ_data['alt_labels']:
                    normalized_alt = self.normalize_label(alt_label)
                    label_index[normalized_alt].append((framework, uri, occ_data))
        
        # Find labels that appear in multiple frameworks
        exact_matches = 0
        for normalized_label, occurrences in label_index.items():
            if len(occurrences) > 1:
                # Group by framework
                by_framework = defaultdict(list)
                for framework, uri, occ_data in occurrences:
                    by_framework[framework].append((uri, occ_data))
                
                # Only count if it appears in multiple frameworks
                if len(by_framework) > 1:
                    original_label = occurrences[0][2]['label']
                    self.mappings[original_label]['type'] = 'exact'
                    self.mappings[original_label]['confidence'] = 1.0
                    
                    for framework, occs in by_framework.items():
                        for uri, occ_data in occs:
                            self.mappings[original_label][framework].append({
                                'uri': uri,
                                'label': occ_data['label']
                            })
                    
                    exact_matches += 1
        
        print(f"  ✓ Found {exact_matches} exact matches")
        return exact_matches
    
    def find_fuzzy_matches(self, threshold: float = 0.85):
        """Find fuzzy matches using similarity threshold"""
        print(f"\nFinding fuzzy matches (threshold: {threshold})...")
        
        fuzzy_matches = 0
        
        # Compare all pairs of occupations
        frameworks = ['ca', 'esco', 'onet', 'sg']
        
        for i, fw1 in enumerate(frameworks):
            for fw2 in frameworks[i+1:]:
                for uri1, occ1 in self.occupations[fw1].items():
                    for uri2, occ2 in self.occupations[fw2].items():
                        similarity = self.calculate_similarity(occ1['label'], occ2['label'])
                        
                        if similarity >= threshold and similarity < 1.0:
                            # Check if not already in exact matches
                            label_key = f"{occ1['label']} ~ {occ2['label']}"
                            
                            if label_key not in self.mappings:
                                self.mappings[label_key]['type'] = 'fuzzy'
                                self.mappings[label_key]['confidence'] = similarity
                                self.mappings[label_key][fw1].append({
                                    'uri': uri1,
                                    'label': occ1['label']
                                })
                                self.mappings[label_key][fw2].append({
                                    'uri': uri2,
                                    'label': occ2['label']
                                })
                                fuzzy_matches += 1
        
        print(f"  ✓ Found {fuzzy_matches} fuzzy matches")
        return fuzzy_matches
    
    def generate_owl_mappings(self, output_file: Path):
        """Generate OWL sameAs mappings in Turtle format"""
        print(f"\nGenerating OWL mappings to {output_file}...")
        
        g = Graph()
        g.bind('dv', DV)
        g.bind('dv-occ', DV_OCC)
        g.bind('owl', OWL)
        g.bind('rdfs', RDFS)
        
        mapping_count = 0
        
        for label, mapping_data in self.mappings.items():
            if mapping_data.get('type') == 'exact':
                # Create a unified Dechivo occupation URI
                normalized_id = self.normalize_label(label).replace(' ', '_').replace('/', '_')
                dechivo_uri = DV_OCC[normalized_id]
                
                # Add label
                g.add((dechivo_uri, RDFS.label, label))
                g.add((dechivo_uri, RDF.type, DV.Occupation))
                
                # Add sameAs relationships
                for framework in ['ca', 'esco', 'onet', 'sg']:
                    if framework in mapping_data and mapping_data[framework]:
                        for occ in mapping_data[framework]:
                            from rdflib import URIRef
                            g.add((dechivo_uri, OWL.sameAs, URIRef(occ['uri'])))
                            mapping_count += 1
        
        # Save to file
        g.serialize(destination=str(output_file), format='turtle')
        print(f"  ✓ Generated {mapping_count} owl:sameAs mappings")
    
    def save_json_report(self, output_file: Path):
        """Save mapping results as JSON"""
        print(f"\nSaving JSON report to {output_file}...")
        
        report = {
            'summary': {
                'total_mappings': len(self.mappings),
                'exact_matches': sum(1 for m in self.mappings.values() if m.get('type') == 'exact'),
                'fuzzy_matches': sum(1 for m in self.mappings.values() if m.get('type') == 'fuzzy'),
                'total_occupations_by_framework': {
                    fw: len(occs) for fw, occs in self.occupations.items()
                }
            },
            'mappings': dict(self.mappings)
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✓ Report saved")
    
    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "=" * 80)
        print("ENTITY MAPPING SUMMARY")
        print("=" * 80)
        
        total_exact = sum(1 for m in self.mappings.values() if m.get('type') == 'exact')
        total_fuzzy = sum(1 for m in self.mappings.values() if m.get('type') == 'fuzzy')
        
        print(f"\nTotal unique mappings: {len(self.mappings)}")
        print(f"  - Exact matches: {total_exact}")
        print(f"  - Fuzzy matches: {total_fuzzy}")
        
        print(f"\nOccupations by framework:")
        for fw in ['ca', 'esco', 'onet', 'sg']:
            count = len(self.occupations[fw])
            print(f"  - {fw.upper()}: {count}")
        
        # Coverage analysis
        print(f"\nCross-framework coverage:")
        coverage = defaultdict(int)
        for mapping_data in self.mappings.values():
            frameworks_present = sum(1 for fw in ['ca', 'esco', 'onet', 'sg'] if fw in mapping_data

 and mapping_data[fw])
            if frameworks_present > 1:
                coverage[frameworks_present] += 1
        
        for count in sorted(coverage.keys(), reverse=True):
            print(f"  - {count} frameworks: {coverage[count]} occupations")
        
        # Sample mappings
        print(f"\nSample exact matches (first 10):")
        sample_count = 0
        for label, mapping_data in self.mappings.items():
            if mapping_data.get('type') == 'exact' and sample_count < 10:
                frameworks = [fw.upper() for fw in ['ca', 'esco', 'onet', 'sg'] 
                             if fw in mapping_data and mapping_data[fw]]
                print(f"  - {label}")
                print(f"    Frameworks: {', '.join(frameworks)}")
                sample_count += 1


def main():
    print("=" * 80)
    print("ENTITY MAPPING AND RESOLUTION")
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
    
    # Create mapper
    mapper = EntityMapper(data_dir)
    
    # Load data
    mapper.load_occupations()
    
    # Find matches
    mapper.find_exact_matches()
    mapper.find_fuzzy_matches(threshold=0.85)
    
    # Generate outputs
    output_dir = Path(__file__).parent.parent
    mapper.generate_owl_mappings(output_dir / 'occupation_mappings.ttl')
    mapper.save_json_report(output_dir / 'entity_mappings.json')
    
    # Print summary
    mapper.print_summary()
    
    print("\n✅ Entity mapping complete!")
    print("\nGenerated files:")
    print(f"  - {output_dir / 'occupation_mappings.ttl'}")
    print(f"  - {output_dir / 'entity_mappings.json'}")
    print()


if __name__ == '__main__':
    main()
