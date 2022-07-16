
python train.py

## main parameters
--exp_name xlm_en                          # experiment name
--dump_path ./dumped                       # where to store the experiment

## data location / training objective
--data_path $OUTPATH                       # data location
--lgs 'en'                                 # considered languages
--clm_steps ''                             # CLM objective (for training GPT-2 models)
--mlm_steps 'en'                           # MLM objective

## transformer parameters
--emb_dim 2048                             # embeddings / model dimension (2048 is big, reduce if only 16Gb of GPU memory)
--n_layers 12                              # number of layers
--n_heads 16                               # number of heads
--dropout 0.1                              # dropout
--attention_dropout 0.1                    # attention dropout
--gelu_activation true                     # GELU instead of ReLU

## optimization
--batch_size 32                            # sequences per batch
--bptt 256                                 # sequences length  (streams of 256 tokens)
--optimizer adam_inverse_sqrt,lr=0.00010,warmup_updates=30000,beta1=0.9,beta2=0.999,weight_decay=0.01,eps=0.000001  # optimizer (training is quite sensitive to this parameter)
--epoch_size 300000                        # number of sentences per epoch
--max_epoch 100000                         # max number of epochs (~infinite here)
--validation_metrics _valid_en_mlm_ppl     # validation metric (when to save the best model)
--stopping_criterion _valid_en_mlm_ppl,25  # stopping criterion (if criterion does not improve 25 times)
--fp16 true                                # use fp16 training

## bert parameters
--word_mask_keep_rand '0.8,0.1,0.1'        # bert masking probabilities
--word_pred '0.15'                         # predict 15 percent of the words

## There are other parameters that are not specified here (see train.py).
