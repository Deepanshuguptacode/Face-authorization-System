import json
import matplotlib.pyplot as plt
import numpy as np

# Load the test results WITH threshold 0.25
with open('test_results_with_025.json', 'r') as f:
    results = json.load(f)

# Thresholds to analyze
thresholds_to_analyze = [0.25, 0.30, 0.35, 0.40, 0.50, 0.60]

print("="*80)
print("MULTI-THRESHOLD COMPARISON ANALYSIS")
print("="*80)
print("\nThresholds Analyzed: 0.25, 0.30, 0.35, 0.40, 0.50, 0.60")
print("Note: Threshold 0.25 calculated from similarity distributions")
print()

# Prepare data for comparison
comparison_data = {
    'dataset1': {},
    'dataset2': {}
}

for dataset_results in results:
    dataset_name = dataset_results['dataset']
    
    print(f"\n{'='*80}")
    print(f"DATASET: {dataset_name.upper()}")
    print(f"{'='*80}")
    print(f"\nNumber of persons: {dataset_results['num_persons']}")
    print(f"Total images: {dataset_results['num_images']}")
    print(f"Test pairs: {dataset_results['num_positive_pairs']} positive + {dataset_results['num_negative_pairs']} negative")
    print()
    
    print(f"{'Threshold':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'TP':<6} {'FN':<6} {'FP':<6} {'TN':<6}")
    print("-"*100)
    
    dataset_key = dataset_name.lower()
    comparison_data[dataset_key] = {}
    
    for threshold_result in dataset_results['threshold_results']:
        threshold = threshold_result['threshold']
        
        # Check if this is one of our target thresholds (with small tolerance for float comparison)
        is_target = any(abs(threshold - target) < 0.01 for target in thresholds_to_analyze)
        
        if is_target:
            accuracy = threshold_result['accuracy'] * 100
            precision = threshold_result['precision'] * 100
            recall = threshold_result['recall'] * 100
            f1_score = threshold_result['f1_score'] * 100
            tp = threshold_result['tp']
            fn = threshold_result['fn']
            fp = threshold_result['fp']
            tn = threshold_result['tn']
            
            # Find the closest target threshold for labeling
            closest_threshold = min(thresholds_to_analyze, key=lambda x: abs(x - threshold))
            
            print(f"{closest_threshold:<12.2f} {accuracy:<12.2f} {precision:<12.2f} {recall:<12.2f} {f1_score:<12.2f} {tp:<6} {fn:<6} {fp:<6} {tn:<6}")
            
            # Store for plotting
            comparison_data[dataset_key][closest_threshold] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'tp': tp,
                'fn': fn,
                'fp': fp,
                'tn': tn
            }

# Create comprehensive visualization
fig = plt.figure(figsize=(18, 12))

# Define colors for datasets
colors = ['#3498db', '#e74c3c']
dataset_labels = ['Dataset 1', 'Dataset 2']

# Plot 1: Accuracy Comparison
plt.subplot(3, 3, 1)
for idx, (dataset_key, label, color) in enumerate(zip(['dataset1', 'dataset2'], dataset_labels, colors)):
    thresholds = sorted(comparison_data[dataset_key].keys())
    accuracies = [comparison_data[dataset_key][t]['accuracy'] for t in thresholds]
    plt.plot(thresholds, accuracies, marker='o', linewidth=2, label=label, color=color)
    # Mark the best threshold
    max_acc_idx = accuracies.index(max(accuracies))
    plt.plot(thresholds[max_acc_idx], accuracies[max_acc_idx], 'g*', markersize=15)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('Accuracy (%)', fontsize=11)
plt.title('Accuracy vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

# Plot 2: Precision Comparison
plt.subplot(3, 3, 2)
for dataset_key, label, color in zip(['dataset1', 'dataset2'], dataset_labels, colors):
    thresholds = sorted(comparison_data[dataset_key].keys())
    precisions = [comparison_data[dataset_key][t]['precision'] for t in thresholds]
    plt.plot(thresholds, precisions, marker='s', linewidth=2, label=label, color=color)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('Precision (%)', fontsize=11)
plt.title('Precision vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)
plt.ylim([95, 101])

# Plot 3: Recall Comparison
plt.subplot(3, 3, 3)
for dataset_key, label, color in zip(['dataset1', 'dataset2'], dataset_labels, colors):
    thresholds = sorted(comparison_data[dataset_key].keys())
    recalls = [comparison_data[dataset_key][t]['recall'] for t in thresholds]
    plt.plot(thresholds, recalls, marker='^', linewidth=2, label=label, color=color)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('Recall (%)', fontsize=11)
plt.title('Recall vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

# Plot 4: F1 Score Comparison
plt.subplot(3, 3, 4)
for dataset_key, label, color in zip(['dataset1', 'dataset2'], dataset_labels, colors):
    thresholds = sorted(comparison_data[dataset_key].keys())
    f1_scores = [comparison_data[dataset_key][t]['f1_score'] for t in thresholds]
    plt.plot(thresholds, f1_scores, marker='D', linewidth=2, label=label, color=color)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('F1 Score (%)', fontsize=11)
plt.title('F1 Score vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

# Plot 5: False Negatives Comparison
plt.subplot(3, 3, 5)
for dataset_key, label, color in zip(['dataset1', 'dataset2'], dataset_labels, colors):
    thresholds = sorted(comparison_data[dataset_key].keys())
    fns = [comparison_data[dataset_key][t]['fn'] for t in thresholds]
    plt.plot(thresholds, fns, marker='v', linewidth=2, label=label, color=color)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('False Negatives', fontsize=11)
plt.title('False Negatives vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

# Plot 6: True Positives Comparison
plt.subplot(3, 3, 6)
for dataset_key, label, color in zip(['dataset1', 'dataset2'], dataset_labels, colors):
    thresholds = sorted(comparison_data[dataset_key].keys())
    tps = [comparison_data[dataset_key][t]['tp'] for t in thresholds]
    plt.plot(thresholds, tps, marker='o', linewidth=2, label=label, color=color)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('True Positives', fontsize=11)
plt.title('True Positives vs Threshold', fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

# Plot 7: Metrics Bar Comparison at Threshold 0.30 (Best)
plt.subplot(3, 3, 7)
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
dataset1_values = [comparison_data['dataset1'][0.30]['accuracy'],
                   comparison_data['dataset1'][0.30]['precision'],
                   comparison_data['dataset1'][0.30]['recall'],
                   comparison_data['dataset1'][0.30]['f1_score']]
dataset2_values = [comparison_data['dataset2'][0.30]['accuracy'],
                   comparison_data['dataset2'][0.30]['precision'],
                   comparison_data['dataset2'][0.30]['recall'],
                   comparison_data['dataset2'][0.30]['f1_score']]

x = np.arange(len(metrics))
width = 0.35

bars1 = plt.bar(x - width/2, dataset1_values, width, label='Dataset 1', color=colors[0], alpha=0.8)
bars2 = plt.bar(x + width/2, dataset2_values, width, label='Dataset 2', color=colors[1], alpha=0.8)

plt.xlabel('Metrics', fontsize=11)
plt.ylabel('Percentage (%)', fontsize=11)
plt.title('Metrics Comparison at Threshold 0.30', fontsize=12, fontweight='bold')
plt.xticks(x, metrics, rotation=15)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.ylim([90, 101])

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

# Plot 8: Accuracy heatmap-style comparison
plt.subplot(3, 3, 8)
thresholds = sorted(comparison_data['dataset1'].keys())
dataset1_acc = [comparison_data['dataset1'][t]['accuracy'] for t in thresholds]
dataset2_acc = [comparison_data['dataset2'][t]['accuracy'] for t in thresholds]

data = [dataset1_acc, dataset2_acc]
im = plt.imshow(data, cmap='RdYlGn', aspect='auto', vmin=50, vmax=100)
plt.colorbar(im, label='Accuracy (%)')
plt.yticks([0, 1], dataset_labels)
plt.xticks(range(len(thresholds)), [f'{t:.2f}' for t in thresholds])
plt.xlabel('Threshold', fontsize=11)
plt.title('Accuracy Heatmap', fontsize=12, fontweight='bold')

# Add text annotations
for i in range(len(dataset_labels)):
    for j in range(len(thresholds)):
        text = plt.text(j, i, f'{data[i][j]:.1f}%',
                       ha="center", va="center", color="black", fontsize=9, fontweight='bold')

# Plot 9: Summary metrics at each threshold for Dataset 1
plt.subplot(3, 3, 9)
thresholds = sorted(comparison_data['dataset1'].keys())
metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1']
dataset1_all_metrics = np.array([
    [comparison_data['dataset1'][t]['accuracy'] for t in thresholds],
    [comparison_data['dataset1'][t]['precision'] for t in thresholds],
    [comparison_data['dataset1'][t]['recall'] for t in thresholds],
    [comparison_data['dataset1'][t]['f1_score'] for t in thresholds]
])

x = np.arange(len(thresholds))
width = 0.2

for i, metric_name in enumerate(metrics_names):
    plt.plot(thresholds, dataset1_all_metrics[i], marker='o', linewidth=2, label=metric_name)

plt.xlabel('Threshold', fontsize=11)
plt.ylabel('Percentage (%)', fontsize=11)
plt.title('Dataset 1 - All Metrics', fontsize=12, fontweight='bold')
plt.legend(fontsize=9)
plt.grid(True, alpha=0.3)
plt.xticks(thresholds_to_analyze)

plt.tight_layout()
plt.savefig('multi_threshold_comparison.png', dpi=300, bbox_inches='tight')
print("\n" + "="*80)
print("Visualization saved as: multi_threshold_comparison.png")
print("="*80)

# Save detailed comparison to JSON
comparison_summary = {
    'thresholds_analyzed': thresholds_to_analyze,
    'datasets': comparison_data,
    'recommendations': {
        'best_threshold': 0.30,
        'reason': 'Highest accuracy with perfect precision and excellent recall',
        'dataset1_best_accuracy': comparison_data['dataset1'][0.30]['accuracy'],
        'dataset2_best_accuracy': comparison_data['dataset2'][0.30]['accuracy']
    }
}

with open('multi_threshold_comparison.json', 'w') as f:
    json.dump(comparison_summary, f, indent=2)

print("\nDetailed comparison saved as: multi_threshold_comparison.json")
print()

# Print summary table
print("\n" + "="*80)
print("SUMMARY TABLE - ALL THRESHOLDS")
print("="*80)
print("\nDATASET 1:")
print("-"*80)
print(f"{'Threshold':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
print("-"*80)
for threshold in sorted(comparison_data['dataset1'].keys()):
    data = comparison_data['dataset1'][threshold]
    marker = " ★ BEST" if threshold == 0.30 else ""
    print(f"{threshold:<12.2f} {data['accuracy']:<12.2f} {data['precision']:<12.2f} {data['recall']:<12.2f} {data['f1_score']:<12.2f}{marker}")

print("\n\nDATASET 2:")
print("-"*80)
print(f"{'Threshold':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
print("-"*80)
for threshold in sorted(comparison_data['dataset2'].keys()):
    data = comparison_data['dataset2'][threshold]
    marker = " ★ BEST" if threshold == 0.30 else ""
    print(f"{threshold:<12.2f} {data['accuracy']:<12.2f} {data['precision']:<12.2f} {data['recall']:<12.2f} {data['f1_score']:<12.2f}{marker}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
