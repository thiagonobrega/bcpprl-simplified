This folder contains a version (ported to python 3) of the bc-pprlSegmentAtomAttack. This attack was employed in :
"Explanation and Answers to Critiques on: Blockchain-based privacy-preserving record linkage"

In the following [link](https://colab.research.google.com/drive/1K0VW7sOYgTo5QZFKageG1ICBGbiqYHCy?usp=sharing), we provide the same code deployed to the google cloud environment. We also like to mention that we implemented a different version of rh. We use the xhash library to provide a faster and wider distribution of '1' . 

xhash randon hasing
---
>       elif (hash_type == 'xrh'):  # Xhash Random hashing
>        for seed in range(num_hash_funct):
>          pos=xxhash.xxh64(q_gram, seed=seed).intdigest() % bf_len
>          rec_bf[pos] = 1
>        
>          if (q_gram not in atom_bf_dict):
>            atom_bf[pos] = 1
>          
>          bit_pos_q_gram_set = bit_pos_q_gram_dict.get(pos, set())
>          bit_pos_q_gram_set.add(q_gram)
>          bit_pos_q_gram_dict[pos] = bit_pos_q_gram_se