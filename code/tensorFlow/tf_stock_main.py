from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import tensorflow as tf

import tf_stock_model


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=1000, type=int,
                    help='number of training steps')
parser.add_argument('--price_norm_factor', default=1000., type=float,
                    help='price normalization factor')


def main(argv):
    args = parser.parse_args(argv[1:])

    # Fetch the data
    (train_x, train_y), (test_x, test_y) = tf_stock_model.load_data()

    # Feature columns describe how to use the input.
    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))

    # Build a DNNRegressor, with 2x20-unit hidden layers, with the feature columns
    # defined above as input.
    model = tf.estimator.DNNRegressor(
      hidden_units=[20, 20], feature_columns=my_feature_columns)


    # Train the Model.
    model.train(input_fn=lambda:tf_stock_model.train_input_fn(train_x, train_y,args.batch_size),
                steps=args.train_steps)

    # Test the Model
    #predictions = model.predict(input_fn=lambda:tf_stock_model.eval_input_fn(test_x, test_y,args.batch_size))    

    # Evaluate the model.
    eval_result = model.evaluate(input_fn=lambda:tf_stock_model.eval_input_fn(test_x, test_y,args.batch_size))


    # The evaluation returns a Python dictionary. The "average_loss" key holds the
    # Mean Squared Error (MSE).
    average_loss = eval_result["average_loss"]

    # Convert MSE to Root Mean Square Error (RMSE).
    print("\n" + 80 * "*")
    print("\nRMS error for the test set: ${:.0f}"
        .format(args.price_norm_factor * average_loss**0.5))

    print (predictions)
    print()
    
if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)
