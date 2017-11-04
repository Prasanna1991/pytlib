from configuration.train_configuration import TrainConfiguration
from data_loading.sampler_factory import SamplerFactory
from data_loading.multi_sampler import MultiSampler
import torch.optim as optim
import torch.nn as nn
from networks.vae import VAE
from loss_functions.vae_loss import vae_loss
import random

# define these things here
use_cuda = False
# todo, replace module based random seed
random.seed(1234)
# loader = SamplerFactory.GetAESampler('/home/ray/Data/KITTI/training',max_frames=200,crop_size=[100,100])
loader = MultiSampler(SamplerFactory.GetAESampler,dict(source='/home/ray/Data/KITTI/training',max_frames=200,crop_size=[100,100]))
model = VAE(encoding_size=128,training=True)

# want to do this before constructing optimizer according to pytroch docs
if use_cuda:
	model.cuda()
# optimizer = optim.SGD(model.parameters(), lr=0.005, momentum=0.9)
optimizer = optim.Adam(model.parameters(),lr=1e-2)
loss = vae_loss

train_config = TrainConfiguration(loader,optimizer,model,loss,use_cuda)
