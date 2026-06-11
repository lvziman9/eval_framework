#!/usr/bin/env python3
"""
Example: How to use the evaluation framework programmatically

This script demonstrates:
1. Converting model output to standard format
2. Running evaluation
3. Comparing multiple models
4. Custom evaluation with specific metrics
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.vrkg4rec_adapter import VRKG4RecAdapter
from adapters.pgpr_adapter import PGPRAdapter
from evaluation import UnifiedEvaluator
import pandas as pd


def example_1_convert_output():
    """Example 1: Convert model output to standard format"""
    print("\n" + "="*60)
    print("Example 1: Convert Model Output")
    print("="*60)
    
    # Initialize adapter
    adapter = VRKG4RecAdapter(dataset_name="ml1m")
    
    # Convert output
    # adapter.convert("/path/to/vrkg4rec/output")
    print("✓ Adapter initialized. Use adapter.convert() to process output.")


def example_2_evaluate_single_model():
    """Example 2: Evaluate a single model"""
    print("\n" + "="*60)
    print("Example 2: Evaluate Single Model")
    print("="*60)
    
    # Create evaluator
    evaluator = UnifiedEvaluator(
        dataset_name="ml1m",
        kg_file="data/ml1m/kg.csv"  # Optional
    )
    
    # Evaluate model
    try:
        metrics = evaluator.evaluate_model("vrkg4rec")
        
        print("\n📊 Evaluation Results:")
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                print(f"  {key:20s}: {value:.4f}")
            else:
                print(f"  {key:20s}: {value}")
    except FileNotFoundError:
        print("⚠ Model output not found. Run adapter first.")


def example_3_compare_models():
    """Example 3: Compare multiple models"""
    print("\n" + "="*60)
    print("Example 3: Compare Multiple Models")
    print("="*60)
    
    evaluator = UnifiedEvaluator("ml1m")
    
    models_to_compare = ["vrkg4rec", "pgpr", "cafe"]
    
    try:
        df = evaluator.compare_models(
            model_names=models_to_compare,
            output_file="results/example_comparison.csv"
        )
        
        print("\n📊 Comparison Table:")
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"⚠ Could not compare models: {e}")


def example_4_custom_evaluation():
    """Example 4: Custom evaluation with specific metrics"""
    print("\n" + "="*60)
    print("Example 4: Custom Evaluation")
    print("="*60)
    
    from evaluation.recsys_metrics import avg_LIR, avg_SEP, avg_ETD
    from evaluation.utils import compute_path_validity, compute_path_diversity
    
    evaluator = UnifiedEvaluator("ml1m")
    
    try:
        # Load model output
        paths_data = evaluator.load_model_output("vrkg4rec")
        
        print("\n📊 Custom Metrics:")
        
        # Compute specific metrics
        lir = avg_LIR(paths_data)
        print(f"  LIR: {lir['Overall']:.4f}")
        
        sep = avg_SEP(paths_data)
        print(f"  SEP: {sep['Overall']:.4f}")
        
        etd = avg_ETD(paths_data)
        print(f"  ETD: {etd['Overall']:.4f}")
        
        diversity = compute_path_diversity(paths_data['pred_paths'])
        print(f"  Path Diversity: {diversity:.4f}")
        
        if evaluator.kg is not None:
            validity = compute_path_validity(paths_data['pred_paths'], kg=evaluator.kg)
            print(f"  Path Validity: {validity:.4f}")
        
    except FileNotFoundError:
        print("⚠ Model output not found.")


def example_5_batch_processing():
    """Example 5: Batch processing multiple datasets"""
    print("\n" + "="*60)
    print("Example 5: Batch Processing")
    print("="*60)
    
    datasets = ["ml1m", "lastfm"]
    models = ["vrkg4rec", "pgpr"]
    
    all_results = []
    
    for dataset in datasets:
        print(f"\n📂 Processing {dataset}...")
        evaluator = UnifiedEvaluator(dataset)
        
        for model in models:
            try:
                metrics = evaluator.evaluate_model(model)
                all_results.append(metrics)
                print(f"  ✓ {model}")
            except Exception as e:
                print(f"  ✗ {model}: {e}")
    
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv("results/batch_results.csv", index=False)
        print(f"\n💾 Saved batch results to results/batch_results.csv")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🚀 EVALUATION FRAMEWORK - USAGE EXAMPLES")
    print("="*70)
    
    print("\nSelect an example to run:")
    print("  1. Convert model output to standard format")
    print("  2. Evaluate a single model")
    print("  3. Compare multiple models")
    print("  4. Custom evaluation with specific metrics")
    print("  5. Batch processing multiple datasets")
    print("  6. Run all examples")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    examples = {
        '1': example_1_convert_output,
        '2': example_2_evaluate_single_model,
        '3': example_3_compare_models,
        '4': example_4_custom_evaluation,
        '5': example_5_batch_processing,
    }
    
    if choice == '6':
        for func in examples.values():
            func()
    elif choice in examples:
        examples[choice]()
    else:
        print("Invalid choice.")
    
    print("\n" + "="*70)
    print("✨ Done! Check the code in examples/usage_example.py")
    print("="*70)


if __name__ == '__main__':
    main()
