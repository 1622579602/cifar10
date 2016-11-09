# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Train the CIFAR-10 data"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import os.path
import time

import numpy as np
from six.moves import xrange
import tensorflow as tf

import cifar10

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('train_dir', '/tmp/cifar10_train',
                           """Direct where to write event logs/checkpoint""")

tf.app.flags.DEFINE_integer('max_steps', 3000, """Number of batches""")

tf.app.flags.DEFINE_boolean('log_device_placement', False,
                            """Whether to log device placement""")

def train():
  """Train CIFAR-10 for a number of steps"""
  with tf.Graph().as_default():
    global_step = tf.Variable(0, trainable=False)

    # Get images and labels
    images, labels = cifar10.distorted_inputs()

    # Build a graph that computes the logit predictions from the
    # inference model
    logits = cifar10.inference(images)

    # Calculate loss
    loss = cifar10.loss(logits, labels)

    # Build a graph that trains the model with one batch of examples
    # and updates the model parameters
    train_op = cifar10.train(loss, global_step)

    # Create a saver
    saver = tf.train.Saver(tf.all_variables())

    # Build the summary operation based on the TF collection of Summaries
    summary_op = tf.merge_all_summaries()

    # Initialize variables
    init = tf.initialize_all_variables()

    # Start running operations on the graph
    sess = tf.Session(config=tf.ConfigProto(
      log_device_placement=FLAGS.log_device_placement))
    sess.run(init)

    # Start the queue runners
    tf.train.start_queue_runners(sess=sess)

    summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph)

    for step in xrange(FLAGS.max_steps):
      start_time = time.time()
      _, loss_value = sess.run([train_op, loss])
      duration = time.time() - start_time

      assert not np.isnan(loss_value), 'Model diverged with loss = NaN'

      if step % 10 == 0:
        num_examples_per_step = FLAGS.batch_size
        examples_per_sec = num_examples_per_step / duration
        sec_per_batch = float(duration)

        format_str = ('%s: step %d, loss = %.2f (%.1f examples/sec, %.3f sec/batch)')

        print(format_str % (datetime.now(), step, loss_value, examples_per_sec,
                            sec_per_batch))

        if step % 100 == 0:
          summary_str = sess.run(summary_op)
          summary_writer.add_summary(summary_str, step)

        # Save the model checkpoint periodically
        if step % 1000 == 0 or (step + 1) == FLAGS.max_steps:
          checkpoint_path = os.path.join(FLAGS.train_dir, 'model.ckpt')
          saver.save(sess, checkpoint_path, global_step=step)

def main(argv=None):
  cifar10.maybe_download_and_extract()
  if tf.gfile.Exists(FLAGS.train_dir):
    tf.gfile.DeleteRecursively(FLAGS.train_dir)
  tf.gfile.MakeDirs(FLAGS.train_dir)
  train()

if __name__ == '__main__':
  tf.app.run()
