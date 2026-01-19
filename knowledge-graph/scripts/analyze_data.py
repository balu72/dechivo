#!/usr/bin/env python3
"""
Knowledge Graph Data Analysis Script

Analyzes turtle files from all four frameworks (CA, ESCO, O*NET, SG)
and generates comprehensive statistics about occupations, skills, and relationships.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.namespace import SKOS, DCTERMS
import json
from typing import Dict, List, Set, Tuple

# Define namespaces for each framework
NAMESPACES = {
    'ca': {
        'occ': Namespace('http://data.canada.ca/occupation/'),
        'skill': Namespace('http://data.canada.ca/skill/'),
        'ability': Namespace('http://data.canada.ca/ability/'),
        'knowledge': Namespace('http://data.canada.ca/knowledge/'),
        'activity': Namespace('http://data.canada.ca/workactivity/'),
        'context': Namespace('http://data.canada.ca/workcontext/'),
        'oasis': Namespace('http://data.canada.ca/oasis/'),
    },
    'esco': {
        'base': Namespace('http://data.europa.eu/esco/'),
        'occupation': Namespace('http://data.europa.eu/esco/occupation/'),
        'skill': Namespace('http://data.europa.eu/esco/skill/'),
    },
    'onet': {
        'base': Namespace('http://data.onetcenter.org/'),
        'occupation': Namespace('http://data.onetcenter.org/occupation/'),
        'skill': Namespace('http://data.onetcenter.org/skill/'),
        'knowledge': Namespace('http://data.onetcenter.org/knowledge/'),
        'ability': Namespace('http://data.onetcenter.org/ability/'),
        'technology': Namespace('http://data.onetcenter.org/technology/'),
    },
    'sg': {
        'base': Namespace('http://data.skillsframework.sg/'),
        'occupation': Namespace('http://data.skillsframework.sg/occupation/'),
        'skill': Namespace('http://data.skillsframework.sg/skill/'),
        'competency': Namespace('http://data.skillsframework.sg/competency/'),
        'sector': Namespace('http://data.skillsframework.sg/sector/'),
    }
}


class TurtleAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.stats = {
            'ca': defaultdict(int),
            'esco': defaultdict(int),
            'onet': defaultdict(int),
            'sg': defaultdict(int),
        }
        self.entities = {
            'ca': {'occupations': set(), 'skills': set(), 'abilities': set(), 'knowledge': set()},
            'esco': {'occupations': set(), 'skills': set()},
            'onet': {'occupations': set(), 'skills': set(), 'knowledge': set(), 'abilities': set(), 'technologies': set()},
            'sg': {'occupations': set(), 'skills': set(), 'competencies': set(), 'sectors': set()},
        }
        self.occupation_labels = {
            'ca': [],
            'esco': [],
            'onet': [],
            'sg': [],
        }
        self.errors = []

    def analyze_all(self):
        """Analyze all frameworks"""
        print("=" * 80)
        print("KNOWLEDGE GRAPH DATA ANALYSIS")
        print("=" * 80)
        print()
        
        frameworks = {
            'ca': 'ca_turtle',
            'esco': 'esco_turtle',
            'onet': 'onet_turtle',
            'sg': 'sg_turtle'
        }
        
        for framework_key, dir_name in frameworks.items():
            framework_path = self.data_dir / dir_name
            if framework_path.exists():
                print(f"Analyzing {framework_key.upper()} ({dir_name})...")
                self.analyze_framework(framework_key, framework_path)
                print(f"  ✓ Complete\n")
            else:
                print(f"  ✗ Directory not found: {framework_path}\n")
        
        self.generate_report()

    def analyze_framework(self, framework: str, directory: Path):
        """Analyze all turtle files in a framework directory"""
        ttl_files = list(directory.glob('*.ttl'))
        self.stats[framework]['total_files'] = len(ttl_files)
        
        for ttl_file in ttl_files:
            try:
                self.parse_file(framework, ttl_file)
            except Exception as e:
                error_msg = f"Error parsing {ttl_file.name}: {str(e)}"
                self.errors.append(error_msg)
                print(f"    ⚠ {error_msg}")

    def parse_file(self, framework: str, file_path: Path):
        """Parse a single turtle file"""
        g = Graph()
        g.parse(str(file_path), format='turtle')
        
        if framework == 'ca':
            self.parse_ca(g)
        elif framework == 'esco':
            self.parse_esco(g)
        elif framework == 'onet':
            self.parse_onet(g)
        elif framework == 'sg':
            self.parse_sg(g)

    def parse_ca(self, g: Graph):
        """Parse Canada OASIS files"""
        ns = NAMESPACES['ca']
        
        # Count abilities
        for subj in g.subjects(RDF.type, ns['oasis'].Ability):
            self.entities['ca']['abilities'].add(str(subj))
            label = g.value(subj, RDFS.label)
            if label:
                self.stats['ca']['abilities'] += 1
        
        # Count skills
        for subj in g.subjects(RDF.type, ns['oasis'].Skill):
            self.entities['ca']['skills'].add(str(subj))
            self.stats['ca']['skills'] += 1
        
        # Count knowledge
        for subj in g.subjects(RDF.type, ns['oasis'].Knowledge):
            self.entities['ca']['knowledge'].add(str(subj))
            self.stats['ca']['knowledge'] += 1
        
        # Count occupations
        for subj in g.subjects(RDF.type, ns['oasis'].Occupation):
            self.entities['ca']['occupations'].add(str(subj))
            self.stats['ca']['occupations'] += 1
            label = g.value(subj, RDFS.label)
            if label:
                self.occupation_labels['ca'].append(str(label))

    def parse_esco(self, g: Graph):
        """Parse ESCO files"""
        ns = NAMESPACES['esco']
        
        # Count occupations
        for subj in g.subjects(RDF.type, ns['base'].Occupation):
            self.entities['esco']['occupations'].add(str(subj))
            self.stats['esco']['occupations'] += 1
            label = g.value(subj, RDFS.label)
            if label:
                self.occupation_labels['esco'].append(str(label))
            
            # Count skills for this occupation
            essential_skills = list(g.objects(subj, ns['base'].hasEssentialSkill))
            optional_skills = list(g.objects(subj, ns['base'].hasOptionalSkill))
            
            self.stats['esco']['essential_skills_total'] += len(essential_skills)
            self.stats['esco']['optional_skills_total'] += len(optional_skills)
            
            for skill in essential_skills + optional_skills:
                self.entities['esco']['skills'].add(str(skill))
        
        # Count unique skills
        for subj in g.subjects(RDF.type, ns['base'].Skill):
            self.entities['esco']['skills'].add(str(subj))

    def parse_onet(self, g: Graph):
        """Parse O*NET files"""
        ns = NAMESPACES['onet']
        
        # Count occupations
        for subj in g.subjects(RDF.type, ns['base'].Occupation):
            self.entities['onet']['occupations'].add(str(subj))
            self.stats['onet']['occupations'] += 1
            label = g.value(subj, RDFS.label)
            if label:
                self.occupation_labels['onet'].append(str(label))
            
            # Count skills
            skills = list(g.objects(subj, ns['base'].requiresSkill))
            self.stats['onet']['skills_per_occupation'] += len(skills)
            for skill in skills:
                self.entities['onet']['skills'].add(str(skill))
            
            # Count knowledge
            knowledge = list(g.objects(subj, ns['base'].requiresKnowledge))
            self.stats['onet']['knowledge_per_occupation'] += len(knowledge)
            for k in knowledge:
                self.entities['onet']['knowledge'].add(str(k))
            
            # Count abilities
            abilities = list(g.objects(subj, ns['base'].requiresAbility))
            self.stats['onet']['abilities_per_occupation'] += len(abilities)
            for a in abilities:
                self.entities['onet']['abilities'].add(str(a))
            
            # Count technologies
            technologies = list(g.objects(subj, ns['base'].usesTechnology))
            self.stats['onet']['technologies_per_occupation'] += len(technologies)
            for tech in technologies:
                self.entities['onet']['technologies'].add(str(tech))

    def parse_sg(self, g: Graph):
        """Parse Singapore files"""
        ns = NAMESPACES['sg']
        
        # Count occupations
        for subj in g.subjects(RDF.type, ns['base'].Occupation):
            self.entities['sg']['occupations'].add(str(subj))
            self.stats['sg']['occupations'] += 1
            label = g.value(subj, RDFS.label)
            if label:
                self.occupation_labels['sg'].append(str(label))
            
            # Count skills
            skills = list(g.objects(subj, ns['base'].requiresSkill))
            self.stats['sg']['skills_per_occupation'] += len(skills)
            for skill in skills:
                self.entities['sg']['skills'].add(str(skill))
            
            # Count competencies
            competencies = list(g.objects(subj, ns['base'].requiresCompetency))
            self.stats['sg']['competencies_per_occupation'] += len(competencies)
            for comp in competencies:
                self.entities['sg']['competencies'].add(str(comp))
            
            # Count sectors
            sector = g.value(subj, ns['base'].belongsToSector)
            if sector:
                self.entities['sg']['sectors'].add(str(sector))

    def find_occupation_overlaps(self) -> Dict[str, List[str]]:
        """Find common occupation names across frameworks"""
        overlaps = defaultdict(list)
        
        # Normalize and compare occupation labels
        for fw1 in ['ca', 'esco', 'onet', 'sg']:
            for label1 in self.occupation_labels[fw1]:
                normalized1 = label1.lower().strip()
                found_in = [fw1]
                
                for fw2 in ['ca', 'esco', 'onet', 'sg']:
                    if fw1 != fw2:
                        for label2 in self.occupation_labels[fw2]:
                            normalized2 = label2.lower().strip()
                            if normalized1 == normalized2:
                                found_in.append(fw2)
                
                if len(found_in) > 1:
                    overlaps[label1] = list(set(found_in))
        
        return overlaps

    def generate_report(self):
        """Generate comprehensive statistics report"""
        print("\n" + "=" * 80)
        print("STATISTICS REPORT")
        print("=" * 80)
        print()
        
        # File counts
        print("📁 FILE COUNTS")
        print("-" * 80)
        for framework in ['ca', 'esco', 'onet', 'sg']:
            count = self.stats[framework]['total_files']
            print(f"  {framework.upper():6s}: {count:4d} files")
        print()
        
        # Entity counts
        print("📊 ENTITY COUNTS")
        print("-" * 80)
        
        # Occupations
        print("  Occupations:")
        for framework in ['ca', 'esco', 'onet', 'sg']:
            count = len(self.entities[framework]['occupations'])
            print(f"    {framework.upper():6s}: {count:4d}")
        print()
        
        # Skills
        print("  Skills:")
        for framework in ['ca', 'esco', 'onet', 'sg']:
            count = len(self.entities[framework]['skills'])
            print(f"    {framework.upper():6s}: {count:4d}")
        print()
        
        # Abilities (CA & O*NET only)
        print("  Abilities:")
        print(f"    CA    : {len(self.entities['ca']['abilities']):4d}")
        print(f"    O*NET : {len(self.entities['onet']['abilities']):4d}")
        print()
        
        # Knowledge (CA & O*NET only)
        print("  Knowledge:")
        print(f"    CA    : {len(self.entities['ca']['knowledge']):4d}")
        print(f"    O*NET : {len(self.entities['onet']['knowledge']):4d}")
        print()
        
        # Technologies (O*NET only)
        print(f"  Technologies (O*NET): {len(self.entities['onet']['technologies']):4d}")
        print()
        
        # Competencies (SG only)
        print(f"  Competencies (SG): {len(self.entities['sg']['competencies']):4d}")
        print()
        
        # Sectors (SG only)
        print(f"  Sectors (SG): {len(self.entities['sg']['sectors']):4d}")
        print()
        
        # Averages
        print("📈 AVERAGES PER OCCUPATION")
        print("-" * 80)
        
        # ESCO
        esco_occ_count = len(self.entities['esco']['occupations'])
        if esco_occ_count > 0:
            avg_essential = self.stats['esco']['essential_skills_total'] / esco_occ_count
            avg_optional = self.stats['esco']['optional_skills_total'] / esco_occ_count
            print(f"  ESCO:")
            print(f"    Average Essential Skills: {avg_essential:.1f}")
            print(f"    Average Optional Skills:  {avg_optional:.1f}")
            print()
        
        # O*NET
        onet_occ_count = len(self.entities['onet']['occupations'])
        if onet_occ_count > 0:
            avg_skills = self.stats['onet']['skills_per_occupation'] / onet_occ_count
            avg_knowledge = self.stats['onet']['knowledge_per_occupation'] / onet_occ_count
            avg_abilities = self.stats['onet']['abilities_per_occupation'] / onet_occ_count
            avg_tech = self.stats['onet']['technologies_per_occupation'] / onet_occ_count
            print(f"  O*NET:")
            print(f"    Average Skills:       {avg_skills:.1f}")
            print(f"    Average Knowledge:    {avg_knowledge:.1f}")
            print(f"    Average Abilities:    {avg_abilities:.1f}")
            print(f"    Average Technologies: {avg_tech:.1f}")
            print()
        
        # Singapore
        sg_occ_count = len(self.entities['sg']['occupations'])
        if sg_occ_count > 0:
            avg_skills = self.stats['sg']['skills_per_occupation'] / sg_occ_count
            avg_comp = self.stats['sg']['competencies_per_occupation'] / sg_occ_count
            print(f"  Singapore:")
            print(f"    Average Skills:       {avg_skills:.1f}")
            print(f"    Average Competencies: {avg_comp:.1f}")
            print()
        
        # Occupation overlaps
        print("🔗 OCCUPATION OVERLAPS")
        print("-" * 80)
        overlaps = self.find_occupation_overlaps()
        
        # Count by number of frameworks
        multi_framework_count = defaultdict(int)
        for occ_label, frameworks in overlaps.items():
            multi_framework_count[len(frameworks)] += 1
        
        print(f"  Occupations found in multiple frameworks:")
        for count in sorted(multi_framework_count.keys(), reverse=True):
            if count > 1:
                print(f"    {count} frameworks: {multi_framework_count[count]} occupations")
        print()
        
        # Sample overlaps
        print("  Sample overlapping occupations:")
        sample_count = 0
        for occ_label, frameworks in sorted(overlaps.items()):
            if len(frameworks) > 1 and sample_count < 10:
                frameworks_str = ', '.join(sorted(frameworks))
                print(f"    - {occ_label} ({frameworks_str})")
                sample_count += 1
        print()
        
        # Errors
        if self.errors:
            print("❌ ERRORS")
            print("-" * 80)
            for error in self.errors[:10]:
                print(f"  {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
            print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        total_files = sum(self.stats[fw]['total_files'] for fw in ['ca', 'esco', 'onet', 'sg'])
        total_occupations = sum(len(self.entities[fw]['occupations']) for fw in ['ca', 'esco', 'onet', 'sg'])
        total_skills = sum(len(self.entities[fw]['skills']) for fw in ['ca', 'esco', 'onet', 'sg'])
        
        print(f"  Total Files:       {total_files:5d}")
        print(f"  Total Occupations: {total_occupations:5d}")
        print(f"  Total Skills:      {total_skills:5d}")
        print(f"  Errors:            {len(self.errors):5d}")
        print()
        
        # Save detailed report
        self.save_json_report()
        print("✅ Detailed JSON report saved to: analysis_report.json")
        print()

    def save_json_report(self):
        """Save detailed report as JSON"""
        report = {
            'summary': {
                'total_files': sum(self.stats[fw]['total_files'] for fw in ['ca', 'esco', 'onet', 'sg']),
                'total_occupations': sum(len(self.entities[fw]['occupations']) for fw in ['ca', 'esco', 'onet', 'sg']),
                'total_skills': sum(len(self.entities[fw]['skills']) for fw in ['ca', 'esco', 'onet', 'sg']),
            },
            'by_framework': {
                'ca': {
                    'files': self.stats['ca']['total_files'],
                    'occupations': len(self.entities['ca']['occupations']),
                    'skills': len(self.entities['ca']['skills']),
                    'abilities': len(self.entities['ca']['abilities']),
                    'knowledge': len(self.entities['ca']['knowledge']),
                },
                'esco': {
                    'files': self.stats['esco']['total_files'],
                    'occupations': len(self.entities['esco']['occupations']),
                    'skills': len(self.entities['esco']['skills']),
                },
                'onet': {
                    'files': self.stats['onet']['total_files'],
                    'occupations': len(self.entities['onet']['occupations']),
                    'skills': len(self.entities['onet']['skills']),
                    'knowledge': len(self.entities['onet']['knowledge']),
                    'abilities': len(self.entities['onet']['abilities']),
                    'technologies': len(self.entities['onet']['technologies']),
                },
                'sg': {
                    'files': self.stats['sg']['total_files'],
                    'occupations': len(self.entities['sg']['occupations']),
                    'skills': len(self.entities['sg']['skills']),
                    'competencies': len(self.entities['sg']['competencies']),
                    'sectors': len(self.entities['sg']['sectors']),
                },
            },
            'occupation_overlaps': self.find_occupation_overlaps(),
            'errors': self.errors,
        }
        
        with open('analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)


def main():
    # Get data directory from command line or use default
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Default to parent's parent's data directory
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent.parent / 'data'
    
    if not Path(data_dir).exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)
    
    analyzer = TurtleAnalyzer(data_dir)
    analyzer.analyze_all()


if __name__ == '__main__':
    main()
