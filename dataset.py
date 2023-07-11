from datasets import load_dataset

def get_dataset(dataset_name):
    data = load_dataset(dataset_name, split='train')
    data = data.to_pandas()
    return data
