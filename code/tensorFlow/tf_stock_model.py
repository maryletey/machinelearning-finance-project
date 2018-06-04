import pandas as pd
import tensorflow as tf


def load_data():
    #load data

    train_path = "amd_train.csv"
    test_path = "amd_test.csv"

    train = pd.read_csv(train_path)
    train_x, train_y = train, train.pop('Adj_Close')

    test = pd.read_csv(test_path)
    test_x, test_y = test, test.pop('Adj_Close')

    return (train_x, train_y), (test_x, test_y)

def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the dataset.
    return dataset


def eval_input_fn(features, labels, batch_size):
    """An input function for evaluation or prediction"""
    features=dict(features)
    if labels is None:
        # No labels, use only features.
        inputs = features
    else:
        inputs = (features, labels)

    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)

    # Return the dataset.
    return dataset
