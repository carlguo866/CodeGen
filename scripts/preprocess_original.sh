python -m codegen_sources.preprocessing.preprocess \
/home/carl/CodeGen/data/github3 \
--langs cpp  \
--mode monolingual \
--local_parallelism 30 \
--bpe_mode=fast \
--local=True \
--train_splits=3 \
--fastbpe_code_path /home/carl/CodeGen/data/github3/cpp/cpp.monolingual.codes \
--fastbpe_vocab_path /home/carl/CodeGen/data/github3/cpp/cpp.monolingual.vocab \
