import numpy as np
import os
import pandas as pd
import random
import time

random.seed(time.time())


class StockDataSet(object):
    def __init__(self,
                 stock_sym,
                 input_size=1,
                 output_size=1,
                 num_steps=30,
                 test_ratio=0.1,
                 normalized=True,
                 close_price_only=False):
        self.stock_sym = stock_sym
        self.input_size = input_size
        self.output_size = output_size
        self.num_steps = num_steps
        self.test_ratio = test_ratio
        self.normalized = normalized

        np.set_printoptions(threshold=np.nan)
        np.set_printoptions(precision=2)
        
        # Read csv file
       # raw_df = pd.read_csv(os.path.join("../../../data/datafiles/numerical-initial", "%s.csv" % stock_sym))
        raw_df = pd.read_csv("../../../data/data-cleanup/combined_data_aniq_3.csv")        

        #self.raw_seq_X = [price for tup in raw_df[['Open', 'High', 'Low', 'Close']].values for price in tup]
        # self.raw_seq_y = [price for tup in raw_df[['Close']].values for price in tup]
        # self.raw_seq_X = [price for tup in raw_df[['hp_gtrends', 'hp_Volume', 'hp_Last Price']].values for price in tup]
        gtrends = str(stock_sym) + "_gtrends"
        last_price = str(stock_sym) + "_Last Price"
        

        self.raw_seq_y = [price for tup in raw_df[[last_price]].values for price in tup]
        self.raw_seq_y = np.array(self.raw_seq_y)        
        if self.normalized:
            self.raw_seq_gtrends = [price for tup in raw_df[[gtrends]].values for price in tup]
            self.raw_seq_last_price = [price for tup in raw_df[[last_price]].values for price in tup]

            self.raw_seq_gtrends = np.array(self.raw_seq_gtrends)
            self.raw_seq_last_price = np.array(self.raw_seq_last_price)

            self.mean_price = np.mean(self.raw_seq_last_price)
            self.std_price = np.std(self.raw_seq_last_price)

            for i in range (0,len(self.raw_seq_last_price)):
                self.raw_seq_last_price[i] = (self.raw_seq_last_price[i] - self.mean_price)/self.std_price
                self.raw_seq_y[i] = (self.raw_seq_y[i] - self.mean_price)/self.std_price

            mean_gtrends = np.mean(self.raw_seq_gtrends)
            std_gtrends = np.std(self.raw_seq_gtrends)
            for i in range (0,len(self.raw_seq_gtrends)):
                self.raw_seq_gtrends[i] = (self.raw_seq_gtrends[i] - mean_gtrends)/std_gtrends

            self.train_X, self.train_y, self.test_X, self.test_y = self._prepare_data(self.raw_seq_gtrends,self.raw_seq_last_price,self.raw_seq_y)
            
        else:
            self.raw_seq_X = [price for tup in raw_df[[gtrends,last_price]].values for price in tup]
            self.raw_seq_X = np.array(self.raw_seq_X)
            #print self.raw_seq_X
            
            self.train_X, self.train_y, self.test_X, self.test_y = self._prepare_data(1,self.raw_seq_X,self.raw_seq_y)
        
        print "input length:", len(self.train_X)
        print "output length:", len(self.train_y)
        template = ('\Input is "{}", output "{}"')    

        for pred_dict, expect in zip(self.train_X, self.train_y):
            print(template.format(pred_dict,expect))


    def info(self):
        return "StockDataSet [%s] train: %d test: %d" % (
            self.stock_sym, len(self.train_X), len(self.test_y))

    def _prepare_data(self, seq_gtrends, seq_last_price, seq_y):

        #concatenate features
        if self.normalized:
            #seq_X_comb = np.concatenate([seq_gtrends, seq_last_price])
            seq_X = np.column_stack([seq_gtrends, seq_last_price])            
            #print seq_X
            #seq_X_comb = seq_last_price            
        else:
            seq_X_comb = seq_last_price

        # split into items of input_size
       # seq_X = [np.array(seq_X_comb[i * self.input_size: (i + 1) * self.input_size])
       #        for i in range(len(seq_X_comb) // self.input_size)]

        #print seq_X
        # fixing the input size for output label as 1
        seq_y = [np.array(seq_y[i * self.output_size: (i + 1) * self.output_size])
               for i in range(len(seq_y) // self.output_size)]

        # split into groups of num_steps
        X = np.array([seq_X[i: i + self.num_steps] for i in range(len(seq_X) - self.num_steps)])
        y = np.array([seq_y[i + self.num_steps] for i in range(len(seq_y) - self.num_steps)])

        train_size = int(len(X) * (1.0 - self.test_ratio))
        train_X, test_X = X[:train_size], X[train_size:]
        train_y, test_y = y[:train_size], y[train_size:]
        return train_X, train_y, test_X, test_y

    def generate_one_epoch(self, batch_size):
        num_batches = int(len(self.train_X)) // batch_size
        if batch_size * num_batches < len(self.train_X):
            num_batches += 1

        batch_indices = range(num_batches)
        random.shuffle(batch_indices)
        for j in batch_indices:
            batch_X = self.train_X[j * batch_size: (j + 1) * batch_size]
            batch_y = self.train_y[j * batch_size: (j + 1) * batch_size]
            assert set(map(len, batch_X)) == {self.num_steps}
            yield batch_X, batch_y
