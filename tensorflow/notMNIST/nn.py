# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 16:55:11 2017

@author: sily-
"""

'''
@brief: x->Wx+b->RELU->Wx+b->softmax->y
        with SDG , l2 & learing rate decay
@author: Shylock Hg
@time: 2017/8/23
@email:tcath2s@icloud.com
'''

#import
import numpy as np
import tensorflow as tf
from six.moves import cPickle as pickle
from six.moves import range

#load file to dataset
pickle_file = 'notMNIST.pickle'

with open(pickle_file,'rb') as f:
    save = pickle.load(f)
    #assignment to data set
    train_dataset = save['train_dataset']
    train_labels = save['train_labels']
    valid_dataset = save['valid_dataset']
    valid_labels = save['valid_labels']
    eval_dataset = save['eval_dataset']
    eval_labels = save['eval_labels']
    del save
    #print info
    print('The train data is : {} , {}'.format(train_dataset.shape,train_labels.shape))
    print('The valid data is : {} , {}'.format(valid_dataset.shape,valid_labels.shape))
    print('The eval data is : {} , {}'.format(eval_dataset.shape,eval_labels.shape))

#with gradient descent training, even this much data is prohibitive
#subset the traning data for faster turnaround
train_subdata = 10000

image_size = 28
label_size = 10

def reformat(dataset, labels):
  dataset = dataset.reshape((-1, image_size * image_size)).astype(np.float32)
  # Map 0 to [1.0, 0.0, 0.0 ...], 1 to [0.0, 1.0, 0.0 ...]
  labels = (np.arange(label_size) == labels[:,None]).astype(np.float32)
  return dataset, labels
train_dataset, train_labels = reformat(train_dataset, train_labels)
valid_dataset, valid_labels = reformat(valid_dataset, valid_labels)
eval_dataset, eval_labels = reformat(eval_dataset, eval_labels)
print('Training set', train_dataset.shape, train_labels.shape)
print('Validation set', valid_dataset.shape, valid_labels.shape)
print('Test set', eval_dataset.shape, eval_labels.shape)


batch_size = 128
#set graph
graph = tf.Graph()
with graph.as_default():
    tf_train_dataset = tf.placeholder(tf.float32,shape=(None,image_size*image_size))
    tf_train_labels = tf.placeholder(tf.int32,shape=(None,label_size))
    #tf_valid_dataset = tf.constant(valid_dataset)
    #tf_eval_dataset = tf.constant(eval_dataset)

    weight1 = tf.Variable(tf.truncated_normal([image_size*image_size,image_size]))
    bias1 = tf.Variable(tf.zeros([image_size]))

    o1 = tf.matmul(tf_train_dataset,weight1)+bias1

    o2 = tf.nn.relu(o1)


    weight2 = tf.Variable(tf.truncated_normal([image_size,label_size]))
    bias2 = tf.Variable(tf.zeros([label_size]))

    logits = tf.nn.softmax(tf.matmul(o2,weight2) + bias2)

    #l2 regulazitation loss
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=tf_train_labels,logits=logits))
    l2_loss =loss + 0.00018*tf.nn.l2_loss(weight1) + 0.00018*tf.nn.l2_loss(weight2)

    #decay learing rate
    global_step = tf.Variable(0)  # count the number of steps taken.
    learning_rate = tf.train.exponential_decay(0.5, global_step,100000, 0.016)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(l2_loss,
                                                 global_step=global_step)

#count of training
num_train = 4001


#compute accuracy
def accuracy(predction,labels):
    return 100*(np.sum(np.argmax(predction,1) == np.argmax(labels,1)))/predction.shape[0]

#training with gradient descent method
with tf.Session(graph=graph) as s:
    #init Variables
    s.run(tf.global_variables_initializer())
    print('Initiallized!')
    feed_dict_valid = {
            tf_train_dataset:valid_dataset,
            tf_train_labels:valid_labels
            }
    #run optimizer
    for step in range(num_train):
        offset = (step*batch_size)%(train_labels.shape[0]-batch_size)
        batch_dataset = train_dataset[offset:offset+batch_size]
        batch_labels = train_labels[offset:offset+batch_size]
        feed_dict = {
                tf_train_dataset:batch_dataset,
                tf_train_labels:batch_labels
                }
        _,l,predictions = s.run([optimizer,loss,logits],feed_dict=feed_dict)
        if(step%500 == 0):
            print('Training accuracy is : {}'.format(accuracy(predictions,batch_labels)))
            _,_,predictions_valid = s.run([optimizer,loss,logits],feed_dict=feed_dict_valid)
            print('Valid accuracy is : {}'.format(accuracy(predictions_valid,valid_labels)))
    feed_dict_eval = {
            tf_train_dataset:eval_dataset,
            tf_train_labels:eval_labels
            }
    _,_,predictions_eval = s.run([optimizer,loss,logits],feed_dict=feed_dict_eval)
    print("Eval accuracy is : {}".format(accuracy(predictions_eval,eval_labels)))