from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from networks.conv_stack import ConvolutionStack,TransposedConvolutionStack
from networks.vae import VAE
from networks.mlp import MLP
import torch
import math

# both encodes the image and performs detection on a target box(s)
class EncodingDetector(nn.Module):
    def __init__(self):
        super(EncodingDetector, self).__init__()
        self.vae = VAE()
        self.crosscor_batchnorm = nn.BatchNorm2d(1)
        # self.mlp = MLP(depth=2,sizes=[16,4])

    # assert the input has two elements, first is the crop, second the full frame
    def forward(self, crop, frame):
        recon,mu,logvar = self.vae.forward(crop)
        crop_feature_map = self.vae.get_encoding_feature_map()
        frame_feature_map = self.vae.get_encoder().forward(frame)

        # now compute the convolution of the frame_feature_map against the crop_feature map
        # need to compute these unbatched because we are not using the same filter map for each conv
        batch_size = frame_feature_map.size(0)
        response_maps = []
        for i in range(0,batch_size):
            response = F.conv2d(frame_feature_map[i,:].unsqueeze(0),crop_feature_map[i,:].unsqueeze(0))
            response_maps.append(response.squeeze(0))
        rmap = torch.stack(response_maps,0)
        rmap = self.crosscor_batchnorm(rmap)

        # linear_size = rmap.size(2)*rmap.size(3)

        # out_coords = self.mlp.forward(rmap.view(-1,linear_size))
        # out_coords = F.linear(rmap.view(-1,linear_size),self.linear_weights)
        # out_coords = F.sigmoid(out_coords)
        # now take the response map and turn it into coords
        # import ipdb;ipdb.set_trace()
        # print out.size()

        return recon,mu,logvar,rmap