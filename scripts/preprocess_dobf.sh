python -m codegen_sources.preprocessing.preprocess \
/home/carl/CodeGen/data/github3 \
--langs cpp \
--mode obfuscation \
--local_parallelism 40 \
--local True \
--bpe_mode fast \
--fastbpe_code_path /home/carl/CodeGen/data/github3/cpp.monolingual.codes \
--fastbpe_vocab_path /home/carl/CodeGen/data/github3/cpp.monolingual.vocab \
--train_splits 3