import os
import shutil
import random
from pathlib import Path

def create_dataset(source_dirs, output_dir, num_persons=25, images_per_person=10):
    """
    Create a dataset by randomly selecting persons and images.
    
    Args:
        source_dirs: List of source directories (train, val)
        output_dir: Output directory name
        num_persons: Number of different persons to select
        images_per_person: Number of random images per person
    """
    # Create output directory
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"Removing existing {output_dir}...")
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Collect all person folders from source directories
    all_person_folders = []
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        if source_path.exists():
            person_folders = [f for f in source_path.iterdir() if f.is_dir()]
            all_person_folders.extend(person_folders)
    
    print(f"Total person folders available: {len(all_person_folders)}")
    
    # Filter persons with at least 'images_per_person' images
    valid_persons = []
    for person_folder in all_person_folders:
        images = [f for f in person_folder.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
        if len(images) >= images_per_person:
            valid_persons.append(person_folder)
    
    print(f"Persons with at least {images_per_person} images: {len(valid_persons)}")
    
    # Randomly select persons
    if len(valid_persons) < num_persons:
        print(f"Warning: Only {len(valid_persons)} persons available, using all of them.")
        selected_persons = valid_persons
    else:
        selected_persons = random.sample(valid_persons, num_persons)
    
    print(f"Selected {len(selected_persons)} persons for {output_dir}")
    
    # Copy random images for each selected person
    for person_folder in selected_persons:
        # Get all images from this person
        images = [f for f in person_folder.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
        
        # Randomly select images
        selected_images = random.sample(images, min(images_per_person, len(images)))
        
        # Create person folder in output directory
        output_person_dir = output_path / person_folder.name
        output_person_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy selected images
        for img in selected_images:
            shutil.copy2(img, output_person_dir / img.name)
        
        print(f"  Copied {len(selected_images)} images for {person_folder.name}")
    
    print(f"\nDataset '{output_dir}' created successfully!")
    print(f"Total persons: {len(selected_persons)}")
    print(f"Total images: {len(selected_persons) * images_per_person}")

def main():
    # Set random seed for reproducibility (optional - remove if you want different results each time)
    random.seed(42)
    
    # Source directories
    train_dir = "train"
    val_dir = "val"
    
    # Check if source directories exist
    if not os.path.exists(train_dir):
        print(f"Error: {train_dir} directory not found!")
        return
    if not os.path.exists(val_dir):
        print(f"Error: {val_dir} directory not found!")
        return
    
    # Create two new datasets
    print("=" * 60)
    print("Creating Dataset 1...")
    print("=" * 60)
    create_dataset([train_dir, val_dir], "dataset1", num_persons=25, images_per_person=10)
    
    print("\n" + "=" * 60)
    print("Creating Dataset 2...")
    print("=" * 60)
    create_dataset([train_dir, val_dir], "dataset2", num_persons=25, images_per_person=10)
    
    print("\n" + "=" * 60)
    print("Both datasets created successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
