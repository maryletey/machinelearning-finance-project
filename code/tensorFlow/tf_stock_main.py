from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import tensorflow as tf

import stock_data


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=1000, type=int,
                    help='number of training steps')
parser.add_argument('--price_norm_factor', default=1000., type=float,
                    help='price normalization factor')


def from_dataset(ds):
    return lambda: ds.make_one_shot_iterator().get_next()

def main(argv):
    args = parser.parse_args(argv[1:])

    # Fetch the data
    (train_x, train_y), (test_x, test_y) = stock_data.load_data()

    # Build the training dataset.
    train = (
      stock_data.make_dataset(train_x, train_y)
      # Shuffling with a buffer larger than the data set ensures
      # that the examples are well mixed.
      .shuffle(1000).batch(args.batch_size)
      # Repeat forever
      .repeat())

    # Build the validation dataset.
    test = stock_data.make_dataset(test_x, test_y).batch(args.batch_size)

    # Feature columns describe how to use the input.
    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))

    # Build a DNNRegressor, with 2x20-unit hidden layers, with the feature columns
    # defined above as input.
#    model = tf.estimator.DNNRegressor(
#      hidden_units=[20, 20], feature_columns=my_feature_columns)

    model = tf.estimator.LinearRegressor(feature_columns=my_feature_columns)

    # Train the Model.
    model.train(input_fn=from_dataset(train),steps=args.train_steps)

    # Evaluate the model.
    eval_result = model.evaluate(input_fn=from_dataset(test))

    #test_features only
    test_features = stock_data.make_dataset(test_x).batch(args.batch_size)
    # Test the Model
    predictions = model.predict(input_fn=from_dataset(test_features))    



    # The evaluation returns a Python dictionary. The "average_loss" key holds the
    # Mean Squared Error (MSE).
    average_loss = eval_result["average_loss"]

    # Convert MSE to Root Mean Square Error (RMSE).
    print("\n" + 80 * "*")
    print("\nRMS error for the test set: ${:.0f}"
        .format(args.price_norm_factor * average_loss**0.5))

    #Print predicted vs expected
    template = ('\nPrediction is "{}", expected "{}"')    
    for pred_dict, expect in zip(predictions, test_y):
        print(template.format(pred_dict['predictions'][0],expect))
        
    print()
    
if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)
