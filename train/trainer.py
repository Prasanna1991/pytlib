import torch
from torch.autograd import Variable
from image.visualization import tensor_to_pil_image_array, visualize_pil_array
import argparse
import imp
import os
import time
from datetime import datetime
from utils.logger import Logger
from utils.debug import pp
from utils.directory_tools import mkdir, list_files
from train.batcher import Batcher

class Trainer:

    def __init__(self,model_config,args):
        self.model_config = model_config

        # should use strings, namespace or functions here?
        self.loader = self.model_config.loader
        self.model = self.model_config.model
        self.lossfn = self.model_config.loss
        self.optimizer = self.model_config.optimizer
        self.args = args
        self.iteration = 0

        # initialize logging and model saving
        if self.args.output_dir is not None:
            self.logger = Logger(os.path.join(self.args.output_dir,'train_log.json'))
            if self.args.override:
                mkdir(self.args.output_dir,wipe=True)
            else:
                self.load()
        else:
            self.logger = Logger()

    def save(self):
        state = {}
        state['iteration']=self.iteration+1
        state['state_dict']=self.model.state_dict()
        state['optimizer']=self.optimizer.state_dict()
        with open(os.path.join(self.args.output_dir,'model_{0:08d}.mdl'.format(self.iteration)),'wb') as f:
            torch.save(state,f)

    def load(self):
        # list model files and find the latest_model
        all_models = list_files(self.args.output_dir,ext_filter='.mdl')
        if not all_models:
            print 'No previous checkpoints found!'
            return

        all_models_indexed = [(m,int(m.split('.mdl')[0].split('_')[1])) for m in all_models]
        all_models_indexed.sort(key=lambda x: x[1],reverse=True)
        print 'Loading model from disk: {0}'.format(all_models_indexed[0][0])
        checkpoint = torch.load(all_models_indexed[0][0])
        self.model.load_state_dict(checkpoint['state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.iteration = checkpoint['iteration']

    def train(self):
        for i in range(self.iteration,self.iteration+self.args.iterations):
            # load batch_size number of samples and merge them
            data_list,target_list = [],[]
            for j in range(0,args.batch_size):
                next = self.loader.next()
                data_list.append(next.data)
                target_list.append(next.target)
            batched_data = Batcher.batch(data_list)
            batched_targets = Batcher.batch(target_list)
            if self.args.cuda:
                batched_data = batched_data.cuda()
                batched_targets = batched_targets.cuda()

            # import ipdb;ipdb.set_trace()
            inputs, targets = Variable(batched_data), Variable(batched_targets)

            # if self.args.vinput:
            #     visualize_pil_array(tensor_to_pil_image_array(inputs.data),title='input')

            self.optimizer.zero_grad()
            outputs = self.model(inputs)

            # if self.args.voutput:
                # visualize_pil_array(tensor_to_pil_image_array(outputs.data),title='output')

            loss = self.lossfn(outputs, targets)
            loss.backward()
            self.optimizer.step()

            print 'iteration: {0} loss: {1}'.format(self.iteration,loss.data[0])
            if self.iteration%self.args.save_iter==0:
                self.save()

            self.logger.set('time',time.time())
            self.logger.set('date',str(datetime.now()))
            self.logger.set('loss',loss.data[0])
            self.logger.set('iteration',self.iteration)
            self.logger.dump_line()
            self.iteration+=1


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('-t','--train_config',required=True,type=str,help='the train configuration')
    parser.add_argument('-b','--batch_size',default=1, required=False,type=int,help='the batch_size')
    parser.add_argument('-i','--iterations',required=False, type=int, help='the number of iterations', default=1)
    parser.add_argument('-v','--vinput',required=False,action='store_true', help='visualize input')
    parser.add_argument('-z','--voutput',required=False,action='store_true', help='visualize output')
    parser.add_argument('-o','--output_dir',required=False,type=str, help='the directory to output the model params and logs')
    parser.add_argument('-s','--save_iter',type=int,help='save params every this many iterations',default=1000)
    parser.add_argument('-r','--override',action='store_true',help='if override, the directory will be wiped, otherwise resume from the current dir')
    args=parser.parse_args()

    config_file = imp.load_source('train_config', args.train_config)
    args.cuda = config_file.train_config.cuda
    trainer = Trainer(config_file.train_config,args)
    trainer.train()
