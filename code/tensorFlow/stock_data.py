import pandas as pd
import numpy as np
import tensorflow as tf


#def load_data():
#    #load data
#
#    train_path = "amd_train.csv"
#    test_path = "amd_test.csv"
#
#    train = pd.read_csv(train_path)
#    train_x, train_y = train, train.pop('Adj_Close')
#
#    test = pd.read_csv(test_path)
#    test_x, test_y = test, test.pop('Adj_Close')
#
#    return (train_x, train_y), (test_x, test_y)

def load_data(y_name="Adj_Close", train_fraction=0.95, seed=None):
  """Load the automobile data set and split it train/test and features/label.

  Args:
    y_name: the column to return as the label.
    train_fraction: the fraction of the data set to use for training.
    seed: The random seed to use when shuffling the data. `None` generates a
      unique shuffle every run.
  Returns:
    a pair of pairs where the first pair is the training data, and the second
    is the test data:
    `(x_train, y_train), (x_test, y_test) = load_data(...)`
    `x` contains a pandas DataFrame of features, while `y` contains the label
    array.
  """
  data_path = "amd_train.csv"

  # Load the raw data columns.    
  data = pd.read_csv(data_path)

  # Delete rows with unknowns
  data = data.dropna()

  # Shuffle the data
  np.random.seed(seed)

  # Split the data into train/test subsets.
  x_train = data.sample(frac=train_fraction, random_state=seed)
  x_test = data.drop(x_train.index)

  # Extract the label from the features DataFrame.
  y_train = x_train.pop(y_name)
  y_test = x_test.pop(y_name)

  return (x_train, y_train), (x_test, y_test)

def make_dataset(x, y=None):
    """Create a slice Dataset from a pandas DataFrame and labels"""
    # TODO(markdaooust): simplify this after the 1.4 cut.
    # Convert the DataFrame to a dict
    x = dict(x)

    # Convert the pd.Series to np.arrays
    for key in x:
        x[key] = np.array(x[key])

    items = [x]
    if y is not None:
        items.append(np.array(y, dtype=np.float32))

    # Create a Dataset of slices
    return tf.data.Dataset.from_tensor_slices(tuple(items))


#def train_input_fn(features, labels, batch_size):
#    """An input function for training"""
#    # Convert the inputs to a Dataset.
#    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))
#
#    # Shuffle, repeat, and batch the examples.
#    dataset = dataset.shuffle(1000).repeat().batch(batch_size)
#
#    # Return the dataset.
#    return dataset
#
#
#def eval_input_fn(features, labels, batch_size):
#    """An input function for evaluation or prediction"""
#    features=dict(features)
#    if labels is None:
#        # No labels, use only features.
#        inputs = features
#    else:
#        inputs = (features, labels)
#
#    # Convert the inputs to a Dataset.
#    dataset = tf.data.Dataset.from_tensor_slices(inputs)
#
#    # Batch the examples
#    assert batch_size is not None, "batch_size must not be None"
#    dataset = dataset.batch(batch_size)
#
#    # Return the dataset.
#    return dataset
