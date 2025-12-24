"""Quick test of the analyzer"""
from requirements_analyzer import RequirementsAnalyzer

print("Testing Requirements Analyzer...")
print("-" * 50)

# Create analyzer
analyzer = RequirementsAnalyzer()

# Load file
success = analyzer.load_excel('20231129_L3_System_Reqs_FS.xlsx')
print(f"File loaded: {success}")

if success:
    # Generate statistics
    stats = analyzer.generate_statistics()
    
    print(f"\nTotal requirements: {stats['total_requirements']}")
    print(f"\nCategories ({len(stats['by_category'])}):")
    for cat, count in list(stats['by_category'].items())[:5]:
        print(f"  - {cat}: {count}")
    
    print(f"\nStates ({len(stats['by_state'])}):")
    for state, count in stats['by_state'].items():
        print(f"  - {state}: {count}")
    
    print(f"\nWith analysis comments: {stats['with_analysis_comments']}")
    print(f"With test cases: {stats['with_test_cases']}")
    print(f"With dependencies: {stats['with_dependencies']}")
    
    print("\n" + "=" * 50)
    print("[OK] Test passed!")
else:
    print("[FAIL] Test failed - could not load file")
