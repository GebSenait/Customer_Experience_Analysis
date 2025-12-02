"""
Dependency Check Script for Task 2
Checks if all required dependencies are installed correctly
"""

import sys
import os

def check_dependency(module_name, import_name=None):
    """Check if a module can be imported"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - MISSING: {e}")
        return False
    except Exception as e:
        print(f"⚠ {module_name} - ERROR: {e}")
        return False

def check_spacy_model():
    """Check if spaCy model is installed"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model 'en_core_web_sm' - OK")
        return True
    except OSError:
        print("✗ spaCy model 'en_core_web_sm' - MISSING")
        print("  Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"⚠ spaCy model check - ERROR: {e}")
        return False

def check_data_files():
    """Check if required data files exist"""
    processed_dir = 'data/processed'
    if not os.path.exists(processed_dir):
        print(f"✗ Data directory '{processed_dir}' - MISSING")
        return False
    
    csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"✗ Processed CSV files - MISSING in {processed_dir}")
        return False
    
    print(f"✓ Data files - Found {len(csv_files)} CSV file(s)")
    return True

def main():
    print("="*70)
    print("Task 2 Dependency Check")
    print("="*70)
    print()
    
    all_ok = True
    
    # Check core dependencies
    print("Core Dependencies:")
    print("-" * 70)
    all_ok &= check_dependency("pandas")
    all_ok &= check_dependency("numpy")
    all_ok &= check_dependency("sklearn", "sklearn")
    all_ok &= check_dependency("nltk")
    all_ok &= check_dependency("vaderSentiment")
    all_ok &= check_dependency("textblob")
    print()
    
    # Check NLP dependencies
    print("NLP Dependencies:")
    print("-" * 70)
    torch_ok = check_dependency("torch")
    transformers_ok = check_dependency("transformers")
    spacy_ok = check_dependency("spacy")
    print()
    
    # Check spaCy model
    print("spaCy Model:")
    print("-" * 70)
    if spacy_ok:
        model_ok = check_spacy_model()
    else:
        model_ok = False
        print("⚠ Skipping model check (spaCy not installed)")
    print()
    
    # Check data files
    print("Data Files:")
    print("-" * 70)
    data_ok = check_data_files()
    print()
    
    # Summary
    print("="*70)
    if all_ok and torch_ok and transformers_ok and spacy_ok and model_ok and data_ok:
        print("✓ ALL CHECKS PASSED - Ready to run Task 2!")
        print()
        print("You can now run:")
        print("  python src/task2_main.py")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please fix issues above")
        print()
        if not torch_ok:
            print("For torch issues, try:")
            print("  pip uninstall torch")
            print("  pip install torch --index-url https://download.pytorch.org/whl/cpu")
        if not model_ok:
            print("For spaCy model, run:")
            print("  python -m spacy download en_core_web_sm")
        return 1

if __name__ == '__main__':
    sys.exit(main())

