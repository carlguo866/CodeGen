import matplotlib.pyplot as plt
from itertools import chain
import os
import sys
if __name__ == '__main__': 
    log_reader = open("/home/carl/TransCoder/myoutput/train_mt2.log" , 'r', encoding='utf-8')
    log_reader2= None 
  #  log_reader2 = open("/home/carl/TransCoder/myoutput/old/train8.log" , 'r')
    scores = None 
    scores_train = None
    i=0
    name = sys.argv[1]
    isBT = False
    if not os.path.exists(f'results/{name}'):
        os.mkdir(f"results/{name}")
    for log in log_reader: 
        first = True 
        if (log.find('__log__:') != -1): 
            the_dict = eval(log[log.index('__log__:')+8:])
            if scores == None: 
                scores = dict ( (k , []) for k, _ in the_dict.items() ) 
            for k,v in the_dict.items(): 
                scores[k].append(round(v,2))
        elif (log.find('AE-cpp_sa:') != -1): 
            string = log[log.index('AE-cpp_sa:'):log.index('-  - model LR')]
            the_dict = dict( (a.strip(), float(b.strip())) for a,b in (element.split(":") \
                                    for element in string.split("||")) )
            if scores_train == None: 
                scores_train = dict ( (k , []) for k, _ in the_dict.items() ) 
                scores_train["iteration"] = []
            scores_train['iteration'].append(i)
            i+=1
            for k,v in the_dict.items():
                scores_train[k].append(v)
                     
    prev_epoch = len(scores['epoch'])
    if log_reader2 !=None: 
        for log in log_reader2: 
            if (log.find('__log__:') != -1): 
                the_dict = eval(log[log.index('__log__:')+8:])
                for k,v in the_dict.items(): 
                    if k == 'epoch':
                        scores[k].append(prev_epoch+ v)
                        scores[k].append(round(v,2))
            elif (log.find('AE-cpp_sa:') != -1): 
                string = log[log.index('AE-cpp_sa:'):log.index('-  - model LR')]
                the_dict = dict( (a.strip(), float(b.strip())) for a,b in (element.split(":") \
                                        for element in string.split("||")) )
                scores_train['iteration'].append(i)
                i+=1
                for k,v in the_dict.items():
                    scores_train[k].append(v)
    plt.plot(scores_train['iteration'],scores_train['AE-llvm_sa'], label='llvm_sa')
    plt.plot(scores_train['iteration'],scores_train['AE-cpp_sa'], label='cpp_sa')
    plt.xlabel("iteration")
    plt.ylabel('AE training loss')
    plt.title("AE Training Loss Over Time")
    plt.legend()
    plt.savefig(f"results/{name}/c_llvm_train_loss_ae.png")
    plt.clf()
    
    if isBT: 
        plt.plot(scores_train['iteration'],scores_train['BT-llvm_sa-cpp_sa-llvm_sa'], label='llvm_sa-cpp_sa-llvm_sa')
        plt.plot(scores_train['iteration'],scores_train['BT-cpp_sa-llvm_sa-cpp_sa'], label='cpp_sa-llvm_sa-cpp_sa')
        plt.xlabel("iteration")
        plt.ylabel('BT training loss')
        plt.title("BT Training Loss Over Time")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"results/{name}/c_llvm_train_loss_bt.png")
        plt.clf()
    else: 
        pass
        # plt.plot(scores_train['iteration'],scores_train['MT-llvm_sa-cpp_sa'], label='llvm_sa-cpp_sa')
        # plt.plot(scores_train['iteration'],scores_train['MT-cpp_sa-llvm_sa'], label='cpp_sa-llvm_sa')
        # plt.xlabel("iteration")
        # plt.ylabel('MT training loss')
        # plt.title("MT Training Loss Over Time")
        # plt.legend()
        # plt.tight_layout()
        # plt.savefig(f"results/{name}/c_llvm_train_loss_mt.png")
        # plt.clf()

    plt.plot(scores['epoch'][1:],scores['valid_cpp_sa-llvm_sa_mt_acc'][1:], label='validation accuracy')
    plt.plot(scores['epoch'][1:],scores['test_cpp_sa-llvm_sa_mt_acc'][1:], label='test accuracy')
    plt.xlabel("epoch")
    plt.ylabel('percentage of valid translation in all tokens (higher is better)')
    plt.title("C to LLVM Translation Accuracy")
    plt.legend()
    plt.savefig(f"results/{name}/c_llvm_acc.png")
    plt.clf()

    if 'valid_cpp_sa-llvm_sa_mt_comp_acc' in scores.keys():
        scores['valid_cpp_sa-llvm_sa_mt_comp_acc'] = [i * 100. for i in scores['valid_cpp_sa-llvm_sa_mt_comp_acc']] 
        scores['test_cpp_sa-llvm_sa_mt_comp_acc'] = [i * 100. for i in scores['test_cpp_sa-llvm_sa_mt_comp_acc']]
        plt.plot(scores['epoch'],scores['valid_cpp_sa-llvm_sa_mt_comp_acc'], label='validation compilation accuracy')
        plt.plot(scores['epoch'],scores['test_cpp_sa-llvm_sa_mt_comp_acc'], label='test compilation accuracy')
        plt.xlabel("epoch")
        plt.ylabel('percentage of successful compilation in all test cases')
        plt.ylim([0,100])
        plt.title("C to LLVM Translation Compilation Accuracy")
        plt.savefig(f"results/{name}/c_llvm_comp_acc.png")
        plt.legend()
        plt.clf()
    
    bleu_loss_epoch = [i for i in range(len(scores['valid_cpp_sa-llvm_sa_mt_bleu']))] 

    plt.plot(bleu_loss_epoch,scores['valid_cpp_sa-llvm_sa_mt_bleu'], label='validation bleu')
    plt.plot(bleu_loss_epoch,scores['test_cpp_sa-llvm_sa_mt_bleu'], label='test bleu')
    plt.xlabel("epoch")
    plt.ylabel('translation bleu')
    plt.title("C to LLVM Translation BLEU Score")
    plt.legend()
    plt.savefig(f"results/{name}/c_llvm_bleu.png")
    plt.clf()

    plt.plot(scores['epoch'][1:],scores['valid_llvm_sa-cpp_sa_mt_acc'][1:], label='validation bleu')
    plt.plot(scores['epoch'][1:],scores['test_llvm_sa-cpp_sa_mt_acc'][1:], label='test bleu')
    plt.xlabel("epoch")
    plt.ylabel('translation bleu')
    plt.title("C to LLVM Translation BLEU Score")
    plt.legend()
    plt.savefig(f"results/{name}/llvm_c_acc.png")
    plt.clf()

    plt.plot(scores['epoch'][1:],scores['valid_cpp_sa-llvm_sa_mt_ppl'][1:], label='validation perplexity')
    plt.plot(scores['epoch'][1:],scores['test_cpp_sa-llvm_sa_mt_ppl'][1:], label='test perplexity')
    plt.xlabel("epoch")
    plt.ylabel('translation perplexity (lower is better)')
    plt.title("C to LLVM Translation Perplexity")
    plt.legend()
    plt.savefig(f"results/{name}/c_llvm_ppl.png")