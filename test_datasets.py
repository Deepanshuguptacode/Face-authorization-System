import cv2
import numpy as np
import os
from pathlib import Path
from insightface.app import FaceAnalysis
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from datetime import datetime
import random

# Load ArcFace model
print("Loading ArcFace model...")
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))
print("Model loaded successfully!\n")

def get_embedding(image_path):
    """Extract face embedding from an image"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return None
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_app.get(img)
        
        if not faces:
            return None
        
        # Take the first face (or the largest face)
        face = faces[0]
        return face.normed_embedding
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def cosine_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings"""
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

def test_dataset(dataset_path, num_test_pairs=100):
    """
    Test face recognition on a dataset
    
    Args:
        dataset_path: Path to the dataset folder
        num_test_pairs: Number of positive and negative pairs to test
    
    Returns:
        Dictionary containing test results
    """
    dataset_path = Path(dataset_path)
    print(f"\n{'='*80}")
    print(f"Testing dataset: {dataset_path.name}")
    print(f"{'='*80}")
    
    # Get all person folders
    person_folders = [f for f in dataset_path.iterdir() if f.is_dir()]
    print(f"Number of persons: {len(person_folders)}")
    
    # Load all embeddings
    embeddings_db = {}
    failed_images = []
    
    print("\nLoading embeddings for all images...")
    for person_folder in tqdm(person_folders, desc="Processing persons"):
        person_id = person_folder.name
        embeddings_db[person_id] = []
        
        images = [f for f in person_folder.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
        
        for img_path in images:
            embedding = get_embedding(img_path)
            if embedding is not None:
                embeddings_db[person_id].append({
                    'path': str(img_path),
                    'embedding': embedding
                })
            else:
                failed_images.append(str(img_path))
    
    # Remove persons with no valid embeddings
    embeddings_db = {k: v for k, v in embeddings_db.items() if len(v) > 0}
    
    print(f"\nSuccessfully processed {sum(len(v) for v in embeddings_db.values())} images")
    print(f"Failed to process {len(failed_images)} images")
    
    # Generate test pairs
    print(f"\nGenerating test pairs...")
    positive_pairs = []
    negative_pairs = []
    
    # Positive pairs (same person)
    person_ids = list(embeddings_db.keys())
    for _ in range(num_test_pairs):
        person_id = random.choice(person_ids)
        if len(embeddings_db[person_id]) >= 2:
            img1, img2 = random.sample(embeddings_db[person_id], 2)
            positive_pairs.append({
                'person_id': person_id,
                'img1': img1,
                'img2': img2,
                'label': 1
            })
    
    # Negative pairs (different persons)
    for _ in range(num_test_pairs):
        if len(person_ids) >= 2:
            person1, person2 = random.sample(person_ids, 2)
            img1 = random.choice(embeddings_db[person1])
            img2 = random.choice(embeddings_db[person2])
            negative_pairs.append({
                'person1_id': person1,
                'person2_id': person2,
                'img1': img1,
                'img2': img2,
                'label': 0
            })
    
    print(f"Generated {len(positive_pairs)} positive pairs (same person)")
    print(f"Generated {len(negative_pairs)} negative pairs (different persons)")
    
    # Calculate similarities
    print("\nCalculating similarities...")
    positive_similarities = []
    negative_similarities = []
    
    for pair in tqdm(positive_pairs, desc="Positive pairs"):
        sim = cosine_similarity(pair['img1']['embedding'], pair['img2']['embedding'])
        positive_similarities.append(sim)
    
    for pair in tqdm(negative_pairs, desc="Negative pairs"):
        sim = cosine_similarity(pair['img1']['embedding'], pair['img2']['embedding'])
        negative_similarities.append(sim)
    
    # Calculate metrics for different thresholds
    thresholds = np.arange(0.3, 0.8, 0.05)
    best_threshold = 0.5
    best_accuracy = 0
    
    results = {
        'dataset': dataset_path.name,
        'num_persons': len(person_ids),
        'num_images': sum(len(v) for v in embeddings_db.values()),
        'failed_images': len(failed_images),
        'num_positive_pairs': len(positive_pairs),
        'num_negative_pairs': len(negative_pairs),
        'positive_similarities': {
            'mean': float(np.mean(positive_similarities)),
            'std': float(np.std(positive_similarities)),
            'min': float(np.min(positive_similarities)),
            'max': float(np.max(positive_similarities))
        },
        'negative_similarities': {
            'mean': float(np.mean(negative_similarities)),
            'std': float(np.std(negative_similarities)),
            'min': float(np.min(negative_similarities)),
            'max': float(np.max(negative_similarities))
        },
        'threshold_results': []
    }
    
    print("\nEvaluating at different thresholds...")
    for threshold in thresholds:
        # True Positives: positive pairs with similarity >= threshold
        tp = sum(1 for sim in positive_similarities if sim >= threshold)
        # False Negatives: positive pairs with similarity < threshold
        fn = len(positive_similarities) - tp
        # True Negatives: negative pairs with similarity < threshold
        tn = sum(1 for sim in negative_similarities if sim < threshold)
        # False Positives: negative pairs with similarity >= threshold
        fp = len(negative_similarities) - tn
        
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results['threshold_results'].append({
            'threshold': float(threshold),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'tp': int(tp),
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn)
        })
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold
    
    results['best_threshold'] = float(best_threshold)
    results['best_accuracy'] = float(best_accuracy)
    
    return results, positive_similarities, negative_similarities

def plot_results(results_list, positive_sims_list, negative_sims_list):
    """Plot comparison results for all datasets"""
    fig = plt.figure(figsize=(16, 10))
    
    # Plot 1: Similarity distributions
    plt.subplot(2, 3, 1)
    for i, (results, pos_sims, neg_sims) in enumerate(zip(results_list, positive_sims_list, negative_sims_list)):
        plt.hist(pos_sims, bins=30, alpha=0.5, label=f"{results['dataset']} - Same Person", density=True)
        plt.hist(neg_sims, bins=30, alpha=0.5, label=f"{results['dataset']} - Different Person", density=True)
    plt.xlabel('Cosine Similarity')
    plt.ylabel('Density')
    plt.title('Similarity Score Distributions')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Accuracy vs Threshold
    plt.subplot(2, 3, 2)
    for results in results_list:
        thresholds = [r['threshold'] for r in results['threshold_results']]
        accuracies = [r['accuracy'] for r in results['threshold_results']]
        plt.plot(thresholds, accuracies, marker='o', label=results['dataset'])
        plt.axvline(results['best_threshold'], linestyle='--', alpha=0.5)
    plt.xlabel('Threshold')
    plt.ylabel('Accuracy')
    plt.title('Accuracy vs Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: F1 Score vs Threshold
    plt.subplot(2, 3, 3)
    for results in results_list:
        thresholds = [r['threshold'] for r in results['threshold_results']]
        f1_scores = [r['f1_score'] for r in results['threshold_results']]
        plt.plot(thresholds, f1_scores, marker='s', label=results['dataset'])
    plt.xlabel('Threshold')
    plt.ylabel('F1 Score')
    plt.title('F1 Score vs Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Precision vs Recall
    plt.subplot(2, 3, 4)
    for results in results_list:
        precisions = [r['precision'] for r in results['threshold_results']]
        recalls = [r['recall'] for r in results['threshold_results']]
        plt.plot(recalls, precisions, marker='^', label=results['dataset'])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 5: Mean similarities comparison
    plt.subplot(2, 3, 5)
    datasets = [r['dataset'] for r in results_list]
    pos_means = [r['positive_similarities']['mean'] for r in results_list]
    neg_means = [r['negative_similarities']['mean'] for r in results_list]
    
    x = np.arange(len(datasets))
    width = 0.35
    plt.bar(x - width/2, pos_means, width, label='Same Person', alpha=0.8)
    plt.bar(x + width/2, neg_means, width, label='Different Person', alpha=0.8)
    plt.xlabel('Dataset')
    plt.ylabel('Mean Similarity')
    plt.title('Mean Similarity Comparison')
    plt.xticks(x, datasets)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    # Plot 6: Best accuracy comparison
    plt.subplot(2, 3, 6)
    datasets = [r['dataset'] for r in results_list]
    accuracies = [r['best_accuracy'] for r in results_list]
    thresholds = [r['best_threshold'] for r in results_list]
    
    bars = plt.bar(datasets, accuracies, alpha=0.8, color=['#2ecc71', '#3498db'])
    plt.ylabel('Best Accuracy')
    plt.title('Best Accuracy per Dataset')
    plt.ylim([0, 1.0])
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add threshold labels on bars
    for bar, threshold in zip(bars, thresholds):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'threshold={threshold:.2f}',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f'face_recognition_results_{timestamp}.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as: {plot_filename}")
    
    plt.show()

def print_summary(results_list):
    """Print detailed summary of results"""
    print("\n" + "="*80)
    print("FACE RECOGNITION SYSTEM - TEST RESULTS SUMMARY")
    print("="*80)
    
    for results in results_list:
        print(f"\n{'─'*80}")
        print(f"Dataset: {results['dataset']}")
        print(f"{'─'*80}")
        print(f"Number of persons: {results['num_persons']}")
        print(f"Total images: {results['num_images']}")
        print(f"Failed images: {results['failed_images']}")
        print(f"\nTest pairs:")
        print(f"  - Positive pairs (same person): {results['num_positive_pairs']}")
        print(f"  - Negative pairs (different persons): {results['num_negative_pairs']}")
        
        print(f"\nSimilarity Statistics:")
        print(f"  Same Person (Positive):")
        print(f"    Mean: {results['positive_similarities']['mean']:.4f}")
        print(f"    Std:  {results['positive_similarities']['std']:.4f}")
        print(f"    Range: [{results['positive_similarities']['min']:.4f}, {results['positive_similarities']['max']:.4f}]")
        
        print(f"  Different Persons (Negative):")
        print(f"    Mean: {results['negative_similarities']['mean']:.4f}")
        print(f"    Std:  {results['negative_similarities']['std']:.4f}")
        print(f"    Range: [{results['negative_similarities']['min']:.4f}, {results['negative_similarities']['max']:.4f}]")
        
        print(f"\nBest Performance:")
        print(f"  Threshold: {results['best_threshold']:.2f}")
        print(f"  Accuracy:  {results['best_accuracy']:.2%}")
        
        # Find best threshold result details
        best_result = next(r for r in results['threshold_results'] if r['threshold'] == results['best_threshold'])
        print(f"  Precision: {best_result['precision']:.2%}")
        print(f"  Recall:    {best_result['recall']:.2%}")
        print(f"  F1 Score:  {best_result['f1_score']:.2%}")
        print(f"\n  Confusion Matrix:")
        print(f"    TP: {best_result['tp']:3d}  FP: {best_result['fp']:3d}")
        print(f"    FN: {best_result['fn']:3d}  TN: {best_result['tn']:3d}")

def main():
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Test both datasets
    datasets = ['dataset1', 'dataset2']
    all_results = []
    all_positive_sims = []
    all_negative_sims = []
    
    for dataset in datasets:
        if os.path.exists(dataset):
            results, pos_sims, neg_sims = test_dataset(dataset, num_test_pairs=100)
            all_results.append(results)
            all_positive_sims.append(pos_sims)
            all_negative_sims.append(neg_sims)
        else:
            print(f"\nWarning: Dataset '{dataset}' not found!")
    
    if all_results:
        # Print summary
        print_summary(all_results)
        
        # Save results to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f'test_results_{timestamp}.json'
        with open(results_filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n{'='*80}")
        print(f"Detailed results saved to: {results_filename}")
        
        # Plot results
        print("\nGenerating visualization plots...")
        plot_results(all_results, all_positive_sims, all_negative_sims)
        
        print(f"\n{'='*80}")
        print("Testing completed successfully!")
        print(f"{'='*80}\n")
    else:
        print("\nNo datasets found to test!")

if __name__ == "__main__":
    main()
