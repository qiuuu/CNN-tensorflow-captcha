from vericode import gen_captcha_text_and_image
#from vericode import number
#from vericode import alphabet
#from vericode import ALPHABET 

import numpy as np 
import tensorflow as tf 

import os
from PIL import Image
from random import choice

targetDir = "zhi"
# 图像大小
#IMAGE_HEIGHT = 60
#IMAGE_WIDTH = 160
IMAGE_HEIGHT = 25
IMAGE_WIDTH = 52
MAX_CAPTCHA = 4
print("验证码文本最长字符数", MAX_CAPTCHA)

def convert2gray(img):
	if len(img.shape) > 2 :
		gray = np.mean(img, -1)

		return gray
	else:
		return img

img_list= []
print("the length is : ", len(img_list))

def gen_list():
	'''global j 
	j = j + 1
	
	
	img_path = os.path.join(targetDir,str(j)+'.png')
	
	return img_path'''


	for parent, dirnames, filenames in os.walk(targetDir):
		for filename in filenames:
			if(filename.find(".png") != -1):
				#print("fimame :"+ filename)
				img_list.append(filename.replace(".png",""))

			
			

	return img_list

img_list = gen_list()
def getImage():
	#img = img_list[i]
	img = choice(img_list)
	img_path = os.path.join(targetDir,img+'.png')
	#print("OPEN", img_path)
	#captcha_image = Image.open(targetDir+"\\"+img+".png")
	captcha_image = Image.open(img_path)
	captcha_image = np.array(captcha_image)
	#print("sdfdsdf---", captcha_image.shape)

	return img, captcha_image


#文本转向量

#char_set = number + alphabet +ALPHABET + ['_']
#char_set = 36+ ['_']
#CHAR_SET_LEN = len(char_set)
CHAR_SET_LEN = 37
print(CHAR_SET_LEN)# 63
def text2vec(text):
	text_len = len(text)
	if text_len > MAX_CAPTCHA:
		raise ValueError('验证码最长4个字符')

	vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)

	def char2pos(c):
		if c == '_':
			k = 36
			return k
		k = ord(c) - 48
		if k > 9 :
			k = ord(c) - 55
			'''if k > 35 :
				k = ord(c) - 61
				if k > 61 :
					raise ValueError('No Map')'''

		return k
	for i, c in enumerate(text):
		idx = i * CHAR_SET_LEN + char2pos(c)
		vector[idx] = 1
	return vector


#向量转回文本
def vec2text(vec):
	char_pos = vec.nonzero()[0]
	text = []
	for i, c in enumerate(char_pos):
		char_at_pos = i
		char_idx = c % CHAR_SET_LEN
		if char_idx < 10:
			char_code = char_idx + ord('0')
		elif char_idx <36:
			char_code = char_idx - 10 + ord('A')
		#elif char_idx <62:
		#	char_code = char_idx - 36 + ord('a')
		elif char_idx == 36:
			char_code = ord('_')
		else:
			raise ValueError('error')
		text.append(chr(char_code))
	return "".join(text)


def get_next_batch(batch_size = 76):
	batch_x = np.zeros([batch_size, IMAGE_HEIGHT*IMAGE_WIDTH])
	batch_y = np.zeros([batch_size, MAX_CAPTCHA*CHAR_SET_LEN])





	def wrap_gen_captcha_text_and_image():
		#while True:
		i = 1
		for i in range(108):
			#text, image = gen_captcha_text_and_image()
			text, image = getImage()
			if image.shape == (25, 52, 3):
				return text, image
	for i in range(batch_size):
		#print("sd--BATCH-SIZE--", batch_size)
		#text, image = wrap_gen_captcha_text_and_image()

		text, image = getImage()
		image = convert2gray(image)

		batch_x[i,:] = image.flatten() / 255
		batch_y[i,:] = text2vec(text)

	
		


	return batch_x, batch_y



X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT*IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA*CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32)

#define CNN
def crack_captcha_cnn(w_alpha =  0.01, b_alpha = 0.1):
	x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])


	# 3 conv layer
	w_c1 = tf.Variable(w_alpha*tf.random_normal([3,3,1,32]))
	b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))

	conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1,1,1,1], padding='SAME'),b_c1))
	conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv1 = tf.nn.dropout(conv1, keep_prob)

	w_c2 = tf.Variable(w_alpha*tf.random_normal([3, 3, 32, 64]))
	b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
	conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'),b_c2))
	conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv2 = tf.nn.dropout(conv2, keep_prob)

	w_c3 = tf.Variable(w_alpha*tf.random_normal([3, 3, 64, 64]))
	b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
	conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
	conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv3 = tf.nn.dropout(conv3, keep_prob)

	# Fully connected layer
	#w_d = tf.Variable(w_alpha*tf.random_normal([8*20*64, 1024]))
	w_d = tf.Variable(w_alpha*tf.random_normal([4*7*64, 1024]))
	b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
	dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
	dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
	dense = tf.nn.dropout(dense, keep_prob)

	w_out = tf.Variable(w_alpha*tf.random_normal([1024, MAX_CAPTCHA*CHAR_SET_LEN]))
	b_out = tf.Variable(b_alpha*tf.random_normal([MAX_CAPTCHA*CHAR_SET_LEN]))
	out = tf.add(tf.matmul(dense, w_out), b_out)
	#out = tf.nn.softmax(out)
	return out


def train_crack_captcha_cnn():
	output = crack_captcha_cnn()
	loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))

	'''with tf.name_scope('loss'):
		loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
		tf.summary.scalar('loss', loss_)

	sess = tf.Session()
	merged = tf.summary.merge_all()

	writer = tf.summary.FileWriter('/tmp/logs',sess.graph)

	init =tf.global_variables_initializer()
	sess.run(init)'''



	optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

	predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
	max_idx_p = tf.argmax(predict, 2)
	max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
	correct_pred = tf.equal(max_idx_p, max_idx_l)
	accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

	saver = tf.train.Saver()
	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())

		#writer = tf.train.SummaryWriter("logs/", sess.graph)

		step = 0
	
		while True:
			batch_x, batch_y = get_next_batch(38)
			_, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
	
			print(step, loss_)

			# 每100 step计算一次准确率
			if step % 100== 0:
				batch_x_test, batch_y_test = get_next_batch(38)
				acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})

				print(step, acc)
				print("---ACCURACY--: ", acc)
				# 如果准确率大于50%,保存模型,完成训练
				if acc > 0.98:
					#saver.save(sess, "crack_capcha.model", global_step=step)
					saver.save(sess, "my_crack_capcha.model", global_step=step)
					break
			step += 1

train_crack_captcha_cnn()





















 















