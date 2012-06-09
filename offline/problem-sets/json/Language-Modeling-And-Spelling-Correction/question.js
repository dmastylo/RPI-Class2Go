var __c2g_questions={"metadata":{"title":"Language Modeling and Spelling Correction","open_time":"2012-03-17 0001","soft_close_time":"2012-04-03 2359","hard_close_time":"2012-05-22 2359","duration":"0","retry_delay":"10","maximum_submissions":"5","modified_time":"1335394022319","parameters":{"show_explanations":{"question":"before_hard_close_time","option":"before_soft_close_time","score":"before_soft_close_time"}},"maximum_score":"5"},"preamble":{},"data":{"question_groups":{"question_group":[{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"7b52178db4088bc6f74fe545b14a2815","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We are given the following corpus, similar to the one in lecture but with \"ham\" replaced by \"Sam\" and \"I am Sam\" included twice:<br>\n\n            <ul>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; Sam I am &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I do not like green eggs and Sam &lt;\/s&gt;<\/li>\n<\/ul>\n\nUsing a bigram language model with add-one smoothing, what is P(Sam | am)? Include &lt;s&gt; and  &lt;\/s&gt; in your counts just like any other token.","explanation":"Using a bigram language model with add-one smoothing, $$P(Sam | am) = \\frac{c(am, Sam) + 1}{c(am) + V} = \\frac{2 + 1}{3 + 11} = \\frac{3}{14}$$.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"0065c0c6cfd40373e296e5d00f2067a8","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{3}{14}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"f02626ed6c601ed824d99d241020c61b","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{2}{3}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"7f257d8cf6f371d9ac51aad29381b5a3","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{3}{28}$$","explanation":"Here $$V$$ denotes the size of the vocabulary, which is the number if types in the corpus, not the number of tokens."},{"@attributes":{"id":"c859d48035c909308e5ca08edacd96b2","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{2}{14}$$","explanation":"We add one to all counts, even those which are already non-zero."}]}}}},{"@attributes":{"id":"fb1b7fa21405b70e07ccac751ef7941d","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We are given the following corpus, similar to the one in lecture but with \"ham\" replaced by \"Sam\"  and \"I am Sam\" included twice:<br>\n\n            <ul>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; Sam I am &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I do not like green eggs and Sam &lt;\/s&gt;<\/li>\n<\/ul>\n\nUsing a bigram language model with add-one smoothing, what is P(Sam | eggs)? Include &lt;s&gt; and  &lt;\/s&gt; in your counts just like any other token.","explanation":"Using a bigram language model with add-one smoothing, $$P(Sam | eggs) = \\frac{c(eggs, Sam) + 1}{c(eggs) + V} = \\frac{0 + 1}{1 + 11} = \\frac{1}{12}$$.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"e6c3b0ad86e27b2d2e82caa76d25aa04","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{1}{12}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"ce345b7aeb422723d62b0ed893c03d92","selected_score":"0","unselected_score":"0"},"text":"$$0$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"37b97e447d51104337cb5140df04044b","selected_score":"0","unselected_score":"0"},"text":"$$1$$","explanation":"When we add $$1$$ to each count we must add $$V$$ to the denominator."},{"@attributes":{"id":"7099bfb0d11898298ebd69f705e24769","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{5}{12}$$","explanation":"In the numerator we use $$c(eggs, Sam)$$, not $$c(Sam)$$."}]}}}},{"@attributes":{"id":"a6a88070036dc6018df493ce845e6576","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We are given the following corpus, similar to the one in lecture but with \"ham\" replaced by \"Sam\"  and \"I am Sam\" included twice:<br>\n\n            <ul>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; Sam I am &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I do not like green eggs and Sam &lt;\/s&gt;<\/li>\n<\/ul>\n\nUsing a bigram language model with add-one smoothing, what is P(am | I)? Include &lt;s&gt; and  &lt;\/s&gt; in your counts just like any other token.","explanation":"Using a bigram language model with add-one smoothing, $$P(am | I) = \\frac{c(I, am) + 1}{c(I) + V} = \\frac{3 + 1}{4 + 11} = \\frac{4}{15}$$.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"87f8a221947408d6ac228e80620885c4","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{4}{15}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"4b94c4342d8fde3b08db8970d1a9ba95","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{3}{4}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"8da941ca36a0a298d4d8dddba766619c","selected_score":"0","unselected_score":"0"},"text":"$$1$$","explanation":"When we add one to each count we must add $$V$$ to the denominator."},{"@attributes":{"id":"0f39f79b50fffc484f783cedc9658eb2","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{4}{24}$$","explanation":"The term $$V$$ measures the number of word types in the corpus, not the number of tokens."}]}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"be557108dfe0083df187b0b3e45b9b76","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"Suppose we want to smooth the likelihood term of a noisy channel model of spelling. We are given two words, $$x$$ and $$w$$, where $$x$$ is the same as $$w$$, except the letter $$w_{i-1}$$ in $$w$$ has been miss typed as $$w_{i-1}x_i$$ in $$x$$.\n\nSpecifically, we want to apply add-one smoothing to $$P(x|w)$$, the probability of typing $$w_{i-1}x_i$$ instead of $$w_{i-1}$$, where $$x_i$$ and $$w_{i-1}$$ are single letters.\n\nFor insertions, $$P(x|w) = \\frac{ins[w_{i-1}, x_i]}{c(w_{i-1})}$$, where $$ins[w_{i-1}, x_i]$$ is the number of times that $$x_i$$ is inserted after $$w_{i-1}$$ in the corpus, and $$c(w_{i-1})$$ is the number of times letter $$w_{i-1}$$ appears in our corpus. Again, please note that here $$x_i$$ and $$w_{i-1}$$ are individual letters, not words. \n<p>\nWhat is the formula for $$P(x|w)$$ if we use add-one smoothing to the insertion edit model? Assume the only characters we use are lowercase a-z, that there are $$V$$ word types in our corpus, and $$n$$ total characters, not counting spaces.","explanation":"The distribution $$P(x|w)$$ has $$26$$ entries, one for each possible value of $$x_i$$. Thus, we add $$26$$ total fictional counts to our data, which means we must add $$26$$ to the denominator.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"16399831d1f0bce028ad32170ac541f3","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{ins[w_{i-1}, x_i]}{c(w_{i-1})}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"dc657c6e300521b498bfb5af59ade022","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{ins[w_{i-1}, x_i] + 1}{c(w_{i-1}) + V}$$","explanation":"The number of times we add one is independent of the vocabulary size, so the denominator is not correct."},{"@attributes":{"id":"9c784ae24bec5c24b45fa52ce5967002","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{ins[w_{i-1}, x_i] + 1}{c(w_{i-1}) + 26}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"b09ee0f9fdcee1644ff379acf940a9af","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{ins[w_{i-1}, x_i] + 1}{c(w_{i-1}) + n}$$","explanation":"We compute P(x|w) for each letter, not for each occurrence of a letter in the corpus. Thus, adding $$n$$ to the denominator isn't correct."}]}}}},{"@attributes":{"id":"211b6349a5d19476e07f0e231666f413","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"Suppose we want to smooth the likelihood term of a noisy channel model of spelling. We are given two words, $$x$$ and $$w$$, where $$x$$ is the same as $$w$$, except the two-letter sequence $$w_{i-1}w_i$$ in $$w$$ has been miss typed as just $$w_{i-1}$$ in $$x$$.\n\nWe want to apply add-one smoothing to $$P(x | w)$$, which is the probability of typing $$w_{i-1}$$ instead of $$w_{i-1}w_i$$, where $$w_{i-1}$$ and $$w_i$$ are single letters.\n\nFor deletions, the maximum-likelihood estimate of $$P(x | w) = \\frac{del[w_{i-1}, w_i]}{c(w_{i-1}w_i)}$$, where $$del[w_{i-1}, w_i]$$ is the number of times that letter $$w_i$$ is deleted after letter $$w_{i-1}$$ in the corpus, and $$c(w_{i-1}w_i)$$ is the number of times the two letter sequence $$w_{i-1}w_i$$ appears in our corpus. Please note again that here $$w_{i-1}$$ and $$w_i$$ are individual letters, not whole words. \n<p>\nWhat is the formula for $$P(x | w)$$ if we use add-one smoothing on the deletion edit model? Assume the only characters we use are lowercase a-z, that there are $$V$$ word types in our corpus, and $$n$$ total characters, not counting spaces.","explanation":"The distribution $$P(x|w)$$ has $$26$$ entries, one for each possible value of $$w_i$$. Thus, we add $$26$$ total fictional counts to our data, which means we must add $$26$$ to the denominator.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"9691e9422dda97698c2b9b775e07c95c","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{del[w_{i-1}, w_i]}{c(w_{i-1}w_i)}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"e4c9b907bfd2cc30be69994ef3d5d420","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{del[w_{i-1}, w_i] + 1}{c(w_{i-1}w_i) + V}$$","explanation":"The number of times we add one is independent of the vocabulary size, so the denominator is not correct."},{"@attributes":{"id":"a7c6a1af1b67194a48aba1c813032c1a","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{del[w_{i-1}, w_i] + 1}{c(w_{i-1}w_i) + 26}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"cfe77da859b2f45a315ac803e856723f","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{del[w_{i-1}, w_i] + 1}{c(w_{i-1}w_i) + n}$$","explanation":"We compute P(x|w) for each letter, not for each occurrence of a letter in the corpus. Thus, adding $$n$$ to the denominator isn't correct."}]}}}},{"@attributes":{"id":"5a6c612b24db893c1aa4c4817a749acc","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"Suppose we want to smooth the likelihood term of a noisy channel model of spelling. We are given two words, $$x$$ and $$w$$, where $$x$$ is the same as $$w$$, except that the letter $$w_i$$ in $$w$$ has been miss typed as $$x_i$$ in $$x$$.\n\nWe want to apply add-one smoothing to $$P(x | w)$$, which is the probability of typing $$x_i$$ instead of $$w_i$$, where $$x_i$$ and $$w_i$$ are single letters.\n\nFor substitutions, the maximum-likelihood estimate of $$P(x | w) = \\frac{sub[x_i, w_i]}{c(w_i)}$$, where $$sub[x_i, w_i]$$ is the number of times that $$x_i$$ is substituted for $$w_i$$ in the corpus, and $$c(w_i)$$ is the number of times that the letter $$w_i$$ appears in our corpus. Again, please note that here $$x_i$$ and $$w_i$$ are individual letters, not whole words. \n<p>\nWhat is the formula for $$P(x | w)$$ if we use add-one smoothing on the substitution edit model? Assume the only characters we use are lowercase a-z, that there are $$V$$ word types in our corpus, and $$n$$ total characters, not counting spaces.","explanation":"The distribution $$P(x|w)$$ has $$26$$ entries, one for each possible value of $$x_i$$. Thus, we add $$26$$ total fictional counts to our data, which means we must add $$26$$ to the denominator.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"a165ee42a3df7036dce722b69be97509","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{sub[x_i, w_i]}{c(w_i)}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"e6febc896728dcee72a4807776b4a2a1","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{sub[x_i, w_i] + 1}{c(w_i) + V}$$","explanation":"The number of times we add one is independent of the vocabulary size, so the denominator is not correct."},{"@attributes":{"id":"9b4f1322d1d5ed48a76ed54b5ec5d06d","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{sub[x_i, w_i] + 1}{c(w_i) + 26}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"0e5b1dd96a6bf6b3fa47fc2458e8febd","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{sub[x_i, w_i] + 1}{c(w_i) + n}$$","explanation":"We compute P(x|w) for each letter in the alphabet, not for each occurrence of a letter in the corpus. Thus, adding $$n$$ to the denominator isn't correct."}]}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":{"@attributes":{"id":"0942711dac7795c40307d4689e1166cf","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We are given the following corpus, similar to the one in lecture but with \"ham\" replaced by \"Sam\"  and \"I am Sam\" included twice:<br>\n\n            <ul>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; Sam I am &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I do not like green eggs and Sam &lt;\/s&gt;<\/li>\n<\/ul>\n\nUsing interpolated Kneser-Ney smoothing, what is $$P_{KN}(Sam | am)$$ if we use a discount factor of $$d = 1$$? \n<p>\n<p>Here are some quantities of interest to make this less tedious:\n\n<ul>\n<li> $$c(am, Sam) = 2$$ <\/li>\n<li> $$c(am) = 3$$ <\/li>\n<li>$$c(Sam) = 4$$ <\/li>\n<!--<li> $$|\\{w_{i-1} : c(w_{i-1}, am) > 0\\}| = 1$$ <\/li> -->\n<li> $$|\\{w : c(am, w) > 0\\}| = 2$$\n<li> $$|\\{(w_{j-1}, w_j) : c(w_{j-1}, w_j) > 0\\}| = 14$$\n<li> $$|\\{ w_{i-1} : c(w_{i-1}, \\text{Sam}) > 0 \\}| = 3$$ <\/li>\n<\/ul>\n\nAs a reminder, here is the formula for $$P_{KN}$$:\n\n$$P_{KN}(w_i | w_{i-1}) = \\frac{ \\max(c(w_{i-1}, w_i) - d, 0)}{c(w_{i-1})} + \\lambda(w_{i-1}) P_{CONTINUATION}(w_i)$$\n\nwhere $$\\lambda(w_{i-1}) = \\frac{d}{c(w_{i-1})} |\\{w : c(w_{i-1}, w) > 0 \\}|$$ \nand $$P_{CONTINUATION}(w_i) = \\frac{|\\{w_{i-1} : c(w_{i-1}, w_i) > 0 \\}|} {|\\{(w_{j-1}, w_j) : c(w_{j-1}, w_j) > 0 \\}|}$$","explanation":"$$P_{KN}(Sam | am) = \\frac{ \\max(c(am, Sam) - 1, 0)}{c(am)} +  \\frac{1}{c(am)} |\\{w : c(am, w) > 0 \\}|   \\frac{|\\{w_{i-1} : c(w_{i-1}, Sam) > 0 \\}|} {|\\{(w_{j-1}, w_j) : c(w_{j-1}, w_j) > 0 \\}|} = \\frac{2-1}{3} + \\frac{2}{3}\\cdot\\frac{3}{14}$$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"7a26d7681dcbdac0ef63b249b7589b1c","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{2-1}{3} + \\frac{2}{3}\\cdot\\frac{3}{14}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"70b21dcaca416eede6f5052ce5ae7140","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{1-1}{3} + \\frac{2}{3}\\cdot\\frac{3}{14}$$","explanation":"\"Sam\" occurs two times in this corpus, so the $$\\frac{1-1}{3}$$ term is incorrect."},{"@attributes":{"id":"a705af3b168016fcfa9e6405bb6844a1","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{2-1}{3} + \\frac{2}{3}\\cdot\\frac{3}{21}$$","explanation":"The $$|\\{(w_{i-1}, w_i) : c(w_{i-1},w_i) > 0\\}|$$ computes the number of unique bigrams in the corpus, not the total number of bigrams."},{"@attributes":{"id":"f68af46c0f1eed91a5a95defe32fee9c","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{2-1}{3} + \\frac{2}{3}\\cdot\\frac{4}{21}$$","explanation":"\"Sam\" has a continuation count of 3, not 4, since \"am Sam\" occurs twice."}]}}}}},{"@attributes":{"select":"1"},"preamble":{},"question":{"@attributes":{"id":"56d548937aa992d8349a4f2510e01141","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We are given the following corpus, similar to the one in lecture but with \"ham\" replaced by \"Sam\" and \"I am Sam\" included twice:<br>\n\n            <ul>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; Sam I am &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I am Sam &lt;\/s&gt;<br><\/li>\n            <li>&lt;s&gt; I do not like green eggs and Sam &lt;\/s&gt;<\/li>\n<\/ul>\n\nIf we use linear interpolation smoothing between a maximum-likelihood bigram model and a maximum-likelihood unigram model with $$\\lambda_1 = \\frac{1}{2}$$ and $$\\lambda_2 = \\frac{1}{2}$$, what is $$P(\\text{Sam} | \\text{am})$$? Include &lt;s&gt; and  &lt;\/s&gt; in your counts just like any other token.","explanation":"$$\\frac{1}{2} P(\\text{Sam}) + \\frac{1}{2} P(\\text{Sam}|\\text{am})= \\frac{1}{2} \\frac{C(\\text{Sam})}{\\sum_{w \\in V} C(w)} +  \\frac{1}{2} \\frac{C(\\text{am, Sam})}{C(\\text{am})} = \\frac{1}{2} \\cdot \\frac{4}{25} + \\frac{1}{2} \\cdot \\frac{2}{3}$$.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"0c7c29211148af2552fe12f340342864","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{1}{2} \\cdot \\frac{4}{25} + \\frac{1}{2} \\cdot \\frac{2}{3}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"fb7f5d4e019d05812c76e3087f2e43d3","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{4}{25}$$","explanation":"This is $$P(\\text{Sam} | \\text{am})$$ using a maximum likelihood bigram model."},{"@attributes":{"id":"f8fab62ad3808c46145ec17895a46fcb","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{1}{2} \\cdot \\frac{4}{17} + \\frac{1}{2} \\cdot \\frac{2}{3}$$","explanation":"We include the start and end of sentence markers in our counts, so there are more than 17 tokens."},{"@attributes":{"id":"128ee2caf25b721946c692aa099cb9ca","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{1}{2} \\cdot \\frac{4}{25} + \\frac{1}{2} \\cdot \\frac{2}{2}$$","explanation":"\"Am\" occurs three times, so the last denominator is incorrect."}]}}}}},{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"cefd17e5b405efb33919e8536a0f055a","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"Suppose we train a bigram language model with add-one smoothing on a given corpus. The corpus contains $$V$$ word types. What is $$P(w_2|w_1)$$, where $$w_2$$ is a word which follows $$w_1$$? We use the notation $$c(w_1, w_2)$$ to denote the number of times that bigram $$(w_1, w_2)$$ occurs in the corpus, and $$c(w_i)$$ is the number of times word $$w_i$$ occurs.","explanation":"Although there are $$V^2$$ possible bigrams in the corpus, we are only interested in bigrams which start with $$w_1$$. Thus, we add one to each of the $$V$$ values for $$P(w_2|w_1)$$, meaning we add $$V$$ to the denominator.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"3fb50629de69d2607113e3a2cc8e641f","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1,w_2)}{c(w_1)}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"a33aa738db750ebe4e7fdffe44c42b10","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2) + 1}{c(w_1) + V}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"f19004ab7cb9d4e44398d37845ea52f5","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2) + 1}{c(w_1) + V^2}$$","explanation":"Although there are $$V^2$$ possible bigrams in the corpus, we are only interested in bigrams which start with $$w_1$$."},{"@attributes":{"id":"64b53a5b1a58eed03b2d61c2582daca3","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2) + V}{c(w_1) + V^2}$$","explanation":"We only add one to each term, not $$V$$."}]}}}},{"@attributes":{"id":"b87fa2a7ad3655daec97d1b226ec5908","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"Suppose we train a trigram language model with add-one smoothing on a given corpus. The corpus contains $$V$$ word types. What is $$P(w_3|w_1, w_2)$$, where $$w_3$$ is a word which follows the bigram $$(w_1, w_2)$$? We use the notation $$c(w_1, w_2, w_3)$$ to denote the number of times that trigram $$(w_1, w_2, w_3)$$ occurs in the corpus, and so on for bigrams and unigrams.","explanation":"Although there are $$V^3$$ possible trigrams in the corpus, we are only interested in bigrams which start with $$(w_1, w_2)$$. Thus, we add one to each of the $$V$$ values for $$P(w_3|w_1, w_2)$$, meaning we must add $$V$$ to the denominator.","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"1dd1a64615fe2142de3eac4223605886","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1,w_2, w_3)}{c(w_1, w_2)}$$","explanation":"This is the maximum-likelihood estimate."},{"@attributes":{"id":"1500d695fd6aad19c491c939bc85108a","selected_score":"1","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2, w_3) + 1}{c(w_1, w_2) + V}$$","explanation":"This is the correct answer."},{"@attributes":{"id":"1ae5f5f27a5387ea48c236ca09ad1de3","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2, w_3) + 1}{c(w_1, w_2) + V^3}$$","explanation":"Although there are $$V^3$$ possible trigrams in the corpus, we are only interested in trigrams which start with $$(w_1, w_2)$$."},{"@attributes":{"id":"a4cbc3ea10efbff2187f2d59c12147e6","selected_score":"0","unselected_score":"0"},"text":"$$\\frac{c(w_1, w_2, w_3) + V}{c(w_1, w_2) + V^3}$$","explanation":"We add $$1$$ to each count, not $$V$$. The normalization is also incorrect."}]}}}}]}]}}};renderQuiz(__c2g_questions);