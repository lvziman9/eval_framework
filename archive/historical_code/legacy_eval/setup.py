"""
Setup script for the evaluation framework.

Usage:
    python setup.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def setup_framework():
    """Setup the evaluation framework"""
    print("\n" + "="*60)
    print("🚀 SETTING UP EXPLAINABILITY BENCHMARK FRAMEWORK")
    print("="*60)
    
    # Create .gitkeep files for empty directories
    print("\n📁 Creating directory structure...")
    empty_dirs = ['data', 'models', 'outputs', 'results/figures']
    for dir_path in empty_dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / '.gitkeep'
        gitkeep.touch()
        print(f"  ✓ {dir_path}")
    
    # Make scripts executable
    print("\n🔧 Making scripts executable...")
    scripts = ['scripts/run_all.py', 'scripts/compare_models.py', 'scripts/visualize.py']
    for script in scripts:
        try:
            Path(script).chmod(0o755)
            print(f"  ✓ {script}")
        except Exception as e:
            print(f"  ⚠ Could not make {script} executable: {e}")
    
    # Install dependencies
    install_deps = input("\n📦 Install dependencies from requirements.txt? (y/n): ")
    if install_deps.lower() == 'y':
        success = run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Installing dependencies"
        )
        if not success:
            print("\n⚠ Warning: Some dependencies failed to install")
    
    # Optional: Install PyTorch Geometric
    install_pyg = input("\n🧠 Install PyTorch Geometric for GNN metrics? (y/n): ")
    if install_pyg.lower() == 'y':
        print("\nNote: This requires PyTorch. Make sure PyTorch is installed first.")
        proceed = input("Continue? (y/n): ")
        if proceed.lower() == 'y':
            run_command(
                f"{sys.executable} -m pip install torch-geometric torch-scatter torch-sparse",
                "Installing PyTorch Geometric"
            )
    
    print("\n" + "="*60)
    print("✨ SETUP COMPLETE!")
    print("="*60)
    print("\n📖 Next steps:")
    print("  1. Place your datasets in data/")
    print("  2. Convert model outputs: python adapters/vrkg4rec_adapter.py --help")
    print("  3. Run evaluation: python scripts/run_all.py")
    print("  4. Visualize results: python scripts/visualize.py")
    print("\n💡 See README.md for detailed usage instructions")
    print()


if __name__ == '__main__':
    setup_framework()
