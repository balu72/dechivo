#!/usr/bin/env python3
"""
Cleanup Script - Remove Intermediary Files

This script removes temporary and intermediary files while keeping:
- deduplicated_knowledge_graph.ttl (final version)
- Statistics and documentation files
- Scripts

Can optionally remove source TTL files to save space.
"""

from pathlib import Path
import shutil
import sys

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def cleanup(remove_source_ttl=False):
    """Clean up intermediary files"""
    
    print("="*80)
    print("CLEANUP - Removing Intermediary Files")
    print("="*80)
    print()
    
    base_dir = Path(__file__).parent.parent.parent
    
    files_to_remove = []
    space_freed = 0
    
    # 1. Remove unified_knowledge_graph.ttl (we have deduplicated version)
    unified_file = base_dir / 'data' / 'unified-files' / 'unified_knowledge_graph.ttl'
    if unified_file.exists():
        size = unified_file.stat().st_size
        files_to_remove.append(('Merged (non-deduplicated) KG', unified_file, size))
    
    # 2. Remove log files
    log_files = [
        base_dir / 'knowledge-graph' / 'merge_output.log',
        base_dir / 'knowledge-graph' / 'deduplication.log',
        base_dir / 'knowledge-graph' / 'load_results.log'
    ]
    
    for log_file in log_files:
        if log_file.exists():
            size = log_file.stat().st_size
            files_to_remove.append((f'Log: {log_file.name}', log_file, size))
    
    # 3. Analysis report (if exists)
    analysis_file = base_dir / 'knowledge-graph' / 'analysis_report.json'
    if analysis_file.exists():
        size = analysis_file.stat().st_size
        files_to_remove.append(('Analysis report', analysis_file, size))
    
    # 4. Entity mappings (if generated but not needed)
    mapping_files = [
        base_dir / 'knowledge-graph' / 'occupation_mappings.ttl',
        base_dir / 'knowledge-graph' / 'entity_mappings.json'
    ]
    
    for mapping_file in mapping_files:
        if mapping_file.exists():
            size = mapping_file.stat().st_size
            files_to_remove.append((f'Mapping: {mapping_file.name}', mapping_file, size))
    
    # 5. Optional: Remove source TTL files (7,929 files, ~500 MB)
    if remove_source_ttl:
        print("⚠️  WARNING: Also removing source TTL files!")
        print()
        
        ttl_dirs = [
            base_dir / 'data' / 'ca_turtle',
            base_dir / 'data' / 'esco_turtle',
            base_dir / 'data' / 'onet_turtle',
            base_dir / 'data' / 'sg_turtle'
        ]
        
        for ttl_dir in ttl_dirs:
            if ttl_dir.exists():
                # Calculate dir size
                dir_size = sum(f.stat().st_size for f in ttl_dir.rglob('*.ttl'))
                file_count = len(list(ttl_dir.glob('*.ttl')))
                files_to_remove.append((f'TTL directory: {ttl_dir.name} ({file_count} files)', ttl_dir, dir_size))
    
    # Show what will be removed
    print("Files to be removed:")
    print("-" * 80)
    for desc, path, size in files_to_remove:
        print(f"  - {desc:50s} {format_size(size):>15s}")
        space_freed += size
    
    print("-" * 80)
    print(f"Total space to free: {format_size(space_freed)}")
    print()
    
    # Confirm
    if files_to_remove:
        response = input("Proceed with cleanup? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print()
            print("Removing files...")
            removed_count = 0
            
            for desc, path, size in files_to_remove:
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"  ✓ Removed directory: {path.name}")
                    else:
                        path.unlink()
                        print(f"  ✓ Removed: {path.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to remove {path.name}: {e}")
            
            print()
            print("="*80)
            print("CLEANUP COMPLETE!")
            print("="*80)
            print(f"\n✅ Removed {removed_count}/{len(files_to_remove)} items")
            print(f"✅ Freed {format_size(space_freed)} of disk space")
            print()
            print("Files kept:")
            print("  ✓ deduplicated_knowledge_graph.ttl (production file)")
            print("  ✓ merge_statistics.json")
            print("  ✓ deduplication_statistics.json")
            print("  ✓ All documentation files")
            print("  ✓ All scripts")
            if not remove_source_ttl:
                print("  ✓ Source TTL files (for reference)")
            print()
        else:
            print("\n❌ Cleanup cancelled")
    else:
        print("✓ No intermediary files found to remove")
        print()
    
    # Show what's kept in unified-files
    print("="*80)
    print("Files in data/unified-files/:")
    print("="*80)
    
    unified_dir = base_dir / 'data' / 'unified-files'
    if unified_dir.exists():
        for file in sorted(unified_dir.iterdir()):
            if file.is_file():
                size = format_size(file.stat().st_size)
                status = "✓ KEEP" if "deduplicated" in file.name or ".json" in file.name or ".md" in file.name else "  "
                print(f"  {status} {file.name:45s} {size:>15s}")
    
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up intermediary KG files')
    parser.add_argument('--remove-source', action='store_true',
                       help='Also remove source TTL files (saves ~500 MB)')
    
    args = parser.parse_args()
    
    if args.remove_source:
        print()
        print("⚠️  WARNING: You are about to remove the source TTL files!")
        print("   This will save ~500 MB but you won't be able to regenerate")
        print("   the knowledge graph without re-downloading the data.")
        print()
        response = input("Are you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Cancelled")
            return
    
    cleanup(remove_source_ttl=args.remove_source)


if __name__ == '__main__':
    main()
