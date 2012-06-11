/**
 * @filename c2gSections.js
 * @description JSON structure which describes section grouping for lecture videos and problem sets 
 */
var sections = [
                {
                heading: "Course Introduction",
                members: [
                   {title: 'Course Introduction',
                    type: 'lecture',
                    contentUrl: 'videos/Course-Introduction/Course-Introduction/index.html'}
                    ]
                },
                {
                heading: "Basic Text Processing",
                members: [
                   {title: 'Regular Expressions', 
                    type: 'lecture',
                    contentUrl:'videos/Basic-Text-Processing/Regular-Expressions/index.html'},
                   {title: 'Regular Expressions in Practical NLP', 
                    type: 'lecture',
                    contentUrl:'videos/Basic-Text-Processing/Regular-Expressions-in-Practical-NLP/index.html'},
                   {title: 'Word Tokenization', 
                    type: 'lecture',
                    contentUrl:'videos/Basic-Text-Processing/Word-Tokenization/index.html'},
                   {title: 'Word Normalization and Stemming', 
                    type: 'lecture',
                    contentUrl:'videos/Basic-Text-Processing/Word-Normalization-and-Stemming/index.html'},
                   {title: 'Sentence Segmentation', 
                    type: 'lecture',
                    contentUrl:'videos/Basic-Text-Processing/Sentence-Segmentation/index.html'},
                   {title: 'Problem Set: Text Processing and Edit Distance', 
                    type: 'ps',
                    contentUrl:'problem-sets/index.html?ps=Text-Processing-And-Edit-Distance'}
                    ]},
                 {
                 heading: "Edit Distance",
                 members: [{title: 'Defining Minimum Edit Distance', 
                    type: 'lecture',
                    contentUrl:'videos/Edit-Distance/Defining-Minimum-Edit-Distance/index.html'},
                 {title: 'Computing Minimum Edit Distance', 
                    type: 'lecture',
                    contentUrl:'videos/Edit-Distance/Computing-Minimum-Edit-Distance/index.html'},
                 {title: 'Backtrace for Computing Alignments', 
                    type: 'lecture',
                    contentUrl:'videos/Edit-Distance/Backtrace-for-Computing-Alignments/index.html'},
                 {title: 'Weighted Minimum Edit Distance', 
                    type: 'lecture',
                    contentUrl:'videos/Edit-Distance/Weighted-Minimum-Edit-Distance/index.html'},
                 {title: 'Minimum Edit Distance in Computational Biology', 
                    type: 'lecture',
                    contentUrl:'videos/Edit-Distance/Minimum-Edit-Distance-in-Computational-Biology/index.html'}
                ]},
                {
                heading: "Language Modeling",
                members: [{title: 'Introduction to N-grams',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Introduction-to-N-grams/index.html'},
                 {title: 'Estimating N-gram Probabilities',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Estimating-N-gram-Probabilities/index.html'},
                 {title: 'Evaluation and Perplexity',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Evaluation-and-Perplexity/index.html'},
                 {title: 'Generalization and Zeros',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Generalization-and-Zeros/index.html'},
                 {title: 'Smoothing: Add-One',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Smoothing--Add-One/index.html'},
                 {title: 'Interpolation',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Interpolation/index.html'},
                 {title: 'Good-Turing Smoothing',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Good-Turing-Smoothing/index.html'},
                 {title: 'Kneser-Ney Smoothing',
                    type: 'lecture',
                    contentUrl:'videos/Language-Modeling/Kneser-Ney-Smoothing/index.html'}]
                },
                {
                heading: "Spelling Correction", 
                members: [{title: 'The Spelling Correction Task',
                    type: 'lecture',
                    videoId: '',
                    contentUrl:'videos/Spelling-Correction/The-Spelling-Correction-Task/index.html'},
                 {title: 'The Noisy Channel Model of Spelling',
                    type: 'lecture',
                    videoId: '',
                    contentUrl:'videos/Spelling-Correction/The-Noisy-Channel-Model-of-Spelling/index.html'},
                 {title: 'Real-Word Spelling Correction',
                    type: 'lecture',
                    videoId: '',
                    contentUrl:'videos/Spelling-Correction/Real-Word-Spelling-Correction/index.html'},
                 {title: 'State of the Art Systems',
                    type: 'lecture',
                    videoId: '',
                    contentUrl:'videos/Spelling-Correction/State-of-the-Art-Systems/index.html'},
                 {title: 'Problem Set: Language Modeling And Spelling Correction', 
                    type: 'ps',
                    contentUrl:'problem-sets/index.html?ps=Language-Modeling-And-Spelling-Correction'}]
                },
                {
                heading: "Text Classification",
                members: [{title: 'What is Text Classification?',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/What-is-Text-Classification/index.html'},
                    {title: 'Naive Bayes',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Naive-Bayes'},
                    {title: 'Formalizing the Naive Bayes Classifier',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Formalizing-the-Naive-Bayes-Classifier/index.html'},
                    {title: 'Naive Bayes: Learning',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Naive-Bayes--Learning'},
                    {title: 'Naive Bayes: Relationship to Language Modeling',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Naive-Bayes--Relationship-to-Language-Modeling/index.html'},
                    {title: 'Multinomial Naive Bayes: A Worked Example',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Multinomial-Naive-Bayes--A-Worked-Example/index.html'},
                    {title: 'Precision, Recall, and the F measure',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Precision--Recall--and-the-F-measure/index.html'},
                    {title: 'Text Classification: Evaluation',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Text-Classification--Evaluation/index.html'},
                    {title: 'Practical Issues in Text Classification',
                    type:'lecture',
                    contentUrl: 'videos/Text-Classification/Practical-Issues-in-Text-Classification/index.html'}
                    ]
                },
                {
                heading:"Sentiment Analysis",
                members: [{title: 'What is Sentiment Analysis?',
                    type: 'lecture',
                    contentUrl: 'videos/Sentiment-Analysis/What-is-Sentiment-Analysis-/index.html'},
                    {title: 'Sentiment Analysis: A baseline algorithm',
                    type: 'lecture',
                    contentUrl: 'videos/Sentiment-Analysis/Sentiment-Analysis--A-baseline-algorithm/index.html'},
                    {title: 'Sentiment Lexicons',
                    type: 'lecture',
                    contentUrl: 'videos/Sentiment-Analysis/Sentiment-Lexicons/index.html'},
                    {title: 'Learning Sentiment Lexicons',
                    type: 'lecture',
                    contentUrl: 'videos/Sentiment-Analysis/Learning-Sentiment-Lexicons/index.html'},
                    {title: 'Other Sentiment Tasks',
                    type: 'lecture',
                    contentUrl: 'videos/Sentiment-Analysis/Other-Sentiment-Tasks'},
                    {title:'Problem Set: Text Classification and Sentiment Analysis',
                    type: 'ps',
                    contentUrl: 'problem-sets/index.html?ps=Text-Classification-And-Sentiment-Analysis'}
                    ]
                },
                {
                heading: "Discriminative classifiers: Maximum Entropy classifiers",
                members: [{title: "Maxent Models and Discriminative Estimation",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Maxent-Models-and-Discriminative-Estimation/index.html"}, 
                    {title: "Discriminative Model Features",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Discriminative-Model-Features/index.html"},
                    {title: "Feature-Based Linear Classifiers",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Feature-Based-Linear-Classifiers/index.html"},
                    {title: "Building a Maxent Model: The Nuts and Bolts",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Building-a-Maxent-Model--The-Nuts-and-Bolts/index.html"},
                    {title: "Generative vs. Discriminative models: The problem of overcounting evidence",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Generative-vs--Discriminative-models--The-problem-of-overcounting-evidence/index.html"},
                    {title: "Maximizing the Likelihood",
                    type: "lecture",
                    contentUrl: "videos/Discriminative-classifiers--Maximum-Entropy-classifiers/Maximizing-the-Likelihood/index.html"}
                    ]
                },
                {
                heading: "Named entity recognition and Maximum Entropy Sequence Models",
                members: [{title: "Introduction to Information Extraction",
                    type: "lecture",
                    contentUrl: "videos/Named-Entity-Recognition-and-Maximum-Entropy-Sequence-Model/Introduction-to-Information-Extraction/index.html"},
                    {title: "Evaluation of Named Entity Recognition",
                    type: "lecture",
                    contentUrl: "videos/Named-Entity-Recognition-and-Maximum-Entropy-Sequence-Model/Evaluation-of-Named-Entity-Recognition/index.html"},
                    {title: "Sequence Models for Named Entity Recognition",
                    type: "lecture",
                    contentUrl: "videos/Named-Entity-Recognition-and-Maximum-Entropy-Sequence-Model/Sequence-Models-for-Named-Entity-Recognition/index.html"},
                    {title: "Maximum Entropy Sequence Models",
                    type: "lecture",
                    contentUrl: "videos/Named-Entity-Recognition-and-Maximum-Entropy-Sequence-Model/Maximum-Entropy-Sequence-Models/index.html"}
                    ]
                },
                {
                heading: "Relation Extraction",
                members: [{title: "What is Relation Extraction?",
                    type: "lecture",
                    contentUrl: "videos/Relation-Extraction/What-is-Relation-Extraction-/index.html"},
                    {title: "Using Patterns to Extract Relations",
                    type: "lecture",
                    contentUrl: "videos/Relation-Extraction/Using-Patterns-to-Extract-Relations/index.html"},
                    {title: "Supervised Relation Extraction",
                    type: "lecture",
                    contentUrl: "videos/Relation-Extraction/Supervised-Relation-Extraction/index.html"},
                    {title: "Semi-Supervised and Unsupervised Relation Extraction",
                    type: "lecture",
                    contentUrl: "videos/Relation-Extraction/Semi-Supervised-and-Unsupervised-Relation-Extraction/index.html"},
                    {title: "Problem Set: Maxent Model and Named Entity Recognition",
                    type: "ps",
                    contentUrl: "problem-sets/index.html?ps=Maxent-Model-And-Named-Entity-Recognition"}
                    ]
                },
                {
                heading: "Advanced Maximum Entropy Models",
                members: [{title: "The Maximum Entropy Model Presentation",
                    type: "lecture",
                    contentUrl: "videos/Advanced-Maximum-Entropy-Models/The-Maximum-Entropy-Model-Presentation/index.html"},
                    {title: "Feature Overlap/Feature Interaction",
                    type: "lecture",
                    contentUrl: "videos/Advanced-Maximum-Entropy-Models/Feature-Overlap-Feature-Interaction/index.html"},
                    {title: "Conditional Maxent Models for Classification",
                    type: "lecture",
                    contentUrl: "videos/Advanced-Maximum-Entropy-Models/Conditional-Maxent-Models-for-Classification/index.html"},
                    {title: "Smoothing/Regularization/Priors for Maxent Models",
                    type: "lecture",
                    contentUrl: "videos/Advanced-Maximum-Entropy-Models/Smoothing-Regularization-Priors-for-Maxent-Models/index.html"}
                    ]
                },
                {
                heading: "POS Tagging",
                members: [
                    {title: "An Intro to Parts of Speech and POS Tagging",
                    type: "lecture",
                    contentUrl: "videos/POS-Tagging/An-Intro-to-Parts-of-Speech-and-POS-Tagging/index.html"},
                    {title: "Some Methods and Results on Sequence Models for POS Tagging",
                    type: "lecture",
                    contentUrl: "videos/POS-Tagging/Some-Methods-and-Results-on-Sequence-Models-for-POS-Tagging/index.html"}
                    ]
                },
                {
                heading: "Parsing Introduction",
                members: [
                    {
                    title: "Syntactic Structure: Constituency vs Dependency",
                    type: "lecture",
                    contentUrl: "videos/Parsing-Introduction/Syntactic-Structure--Constituency-vs-Dependency/index.html"
                    },
                    {
                    title: "Empirical/Data-Driven Approach to Parsing",
                    type: "lecture",
                    contentUrl: "videos/Parsing-Introduction/Empirical-Data-Driven-Approach-to-Parsing/index.html"
                    },
                    {
                    title: "The Exponential Problem in Parsing",
                    type: "lecture",
                    contentUrl: "videos/Parsing-Introduction/The-Exponential-Problem-in-Parsing/index.html"
                    },
                    {
                    title: "Problem Set: Advanced MaxEnt / POS Tagging / Parsing Intro",
                    type: "ps",
                    contentUrl: "problem-sets/index.html?ps=Advanced-Maxent"
                    }
                ]
                },
		/*
                {
                heading: "Instructor Chat",
                members: [
                    {title: "Instructor Chat",
                    type: "lecture",
                    contentUrl: "videos/Instructor-Chat-I/Instructor-Chat/index.html"}
                ]
                },
		*/
                {
                heading: "Probabilistic Parsing",
                members: [
                    {title: "CFGs and PCFGs",
                    type: "lecture",
                    contentUrl: "videos/Probabilistic-Parsing/CFGs-and-PCFGs/index.html"},
                    {title: "Grammar Transforms",
                    type: "lecture",
                    contentUrl: "videos/Probabilistic-Parsing/Grammar-Transforms/index.html"},
                    {title: "CKY Parsing",
                    type: "lecture",
                    contentUrl: "videos/Probabilistic-Parsing/CKY-Parsing/index.html"},
                    {title: "CKY Example",
                    type: "lecture",
                    contentUrl: "videos/Probabilistic-Parsing/CKY-Example/index.html"},
                    {title: "Constituency Parser Evaluation",
                    type: "lecture",
                    contentUrl: "videos/Probabilistic-Parsing/Constituency-Parser-Evaluation/index.html"},
                ]
                },
                {
                heading: "Lexicalized Parsing",
                members: [
                    {
                    title:"Lexicalization of PCFGs",
                    type: "lecture",
                    contentUrl: "videos/Lexicalized-Parsing/Lexicalization-of-PCFGs/index.html"
                    },
                    {
                    title:"Charniak's Model",
                    type: "lecture",
                    contentUrl: "videos/Lexicalized-Parsing/Charniaks-Model/index.html"
                    },
                    {
                    title:"PCFG Independence Assumptions",
                    type: "lecture",
                    contentUrl: "videos/Lexicalized-Parsing/PCFG-Independence-Assumptions/index.html"
                    },
                    {
                    title:"The Return of Unlexicalized PCFGs",
                    type: "lecture",
                    contentUrl: "videos/Lexicalized-Parsing/The-Return-of-Unlexicalized-PCFGs/index.html"
                    },
                    {
                    title:"Latent Variable PCFGs",
                    type: "lecture",
                    contentUrl: "videos/Lexicalized-Parsing/Latent-Variable-PCFGs/index.html"
                    }
                ]
                },
                {
                heading: "Dependency Parsing",
                members: [
                    {
                    title:"Dependency Parsing Introduction",
                    type: "lecture",
                    contentUrl: "videos/Dependency-Parsing/Dependency-Parsing-Introduction/index.html"
                    },
                    {
                    title:"Greedy Transition-Based Parsing",
                    type: "lecture",
                    contentUrl: "videos/Dependency-Parsing/Greedy-Transition-Based-Parsing/index.html"
                    },
                    {
                    title:"Dependencies Encode Relational Structure",
                    type: "lecture",
                    contentUrl: "videos/Dependency-Parsing/Dependencies-Encode-Relational-Structure/index.html"
                    },
                    {
                    title:"Problem Set: Parsing",
                    type: "ps",
                    contentUrl: "problem-sets/index.html?ps=Parsing"
                    }
                ]
                },
                {
                heading: "Information Retrieval",
                members: [
                    {
                    title:"Introduction to Information Retrieval",
                    type: "lecture",
                    contentUrl: "videos/Information-Retrieval/Introduction-to-Information-Retrieval/index.html"
                    },
                    {
                    title:"Term-Document Incidence Matrices",
                    type: "lecture",
                    contentUrl: "videos/Information-Retrieval/Term-Document-Incidence-Matrices/index.html"
                    },
                    {
                    title:"The Inverted Index",
                    type: "lecture",
                    contentUrl: "videos/Information-Retrieval/The-Inverted-Index/index.html"
                    },
                    {
                    title:"Query Processing with the Inverted Index",
                    type: "lecture",
                    contentUrl: "videos/Information-Retrieval/Query-Processing-with-the-Inverted-Index/index.html"
                    },
                    {
                    title:"Phrase Queries and Positional Indexes",
                    type: "lecture",
                    contentUrl: "videos/Information-Retrieval/Phrase-Queries-and-Positional-Indexes/index.html"
                    }
                ]
                },
                {
                heading: "Ranked Information Retrieval",
                members: [
                    {
                    title:"Introducing Ranked Retrieval",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Introducing-Ranked-Retrieval/index.html"
                    },
                    {
                    title:"Scoring with the Jaccard Coefficient",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Scoring-with-the-Jaccard-Coefficient/index.html"
                    },
                    {
                    title:"Term Frequency Weighting",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Term-Frequency-Weighting/index.html"
                    },
                    {
                    title:"Inverse Document Frequency Weighting",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Inverse-Document-Frequency-Weighting/index.html"
                    },
                    {
                    title:"TF-IDF Weighting",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/TF-IDF-Weighting/index.html"
                    },
                    {
                    title:"The Vector Space Model",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/The-Vector-Space-Model/index.html"
                    },
                    {
                    title:"Calculating TF-IDF Cosine Scores",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Calculating-TF-IDF-Cosine-Scores/index.html"
                    },
                    {
                    title:"Evaluating Search Engines",
                    type: "lectures",
                    contentUrl: "videos/Ranked-Information-Retrieval/Evaluating-Search-Engines/index.html"
                    },
                    {
                    title:"Problem Set: Information Retrieval",
                    type: "ps",
                    contentUrl: "problem-sets/index.html?ps=Information-Retrieval"
                    }
                ]
                },
                {
                heading: "Semantics",
                members: [
                    {
                    title:"Word Senses and Word Relations",
                    type: "lecture",
                    contentUrl: "videos/Semantics/Word-Senses-and-Word-Relations/index.html"
                    },
                    {
                    title:"WordNet and Other Online Thesauri",
                    type: "lecture",
                    contentUrl: "videos/Semantics/WordNet-and-Other-Online-Thesauri/index.html"
                    },
                    {
                    title:"Word Similarity and Thesaurus Methods",
                    type: "lecture",
                    contentUrl: "videos/Semantics/Word-Similarity-and-Thesaurus-Methods/index.html"
                    },
                    {
                    title:"Word Similarity: Distributional Similarity I",
                    type: "lecture",
                    contentUrl: "videos/Semantics/Word-Similarity--Distributional-Similarity-I/index.html"
                    },
                    {
                    title:"Word Similarity: Distributional Similarity II",
                    type: "lecture",
                    contentUrl: "videos/Semantics/Word-Similarity--Distributional-Similarity-II/index.html"
                    }
                ]
                },
                {
                heading: "Question Answering",
                members: [
                    {
                    title:"What is Question Answering?",
                    type: "lecture",
                    contentUrl: "videos/Question-Answering/What-is-Question-Answering-/index.html"
                    },
                    {
                    title:"Answer Types and Query Formulation",
                    type: "lecture",
                    contentUrl: "videos/Question-Answering/Answer-Types-and-Query-Formulation/index.html"
                    },
                    {
                    title:"Passage Retrieval and Answer Extraction",
                    type: "lecture",
                    contentUrl: "videos/Question-Answering/Passage-Retrieval-and-Answer-Extraction/index.html"
                    },
                    {
                    title:"Using Knowledge in QA",
                    type: "lecture",
                    contentUrl: "videos/Question-Answering/Using-Knowledge-in-QA/index.html"
                    },
                    {
                    title:"Advanced: Answering Complex Questions",
                    type: "lecture",
                    contentUrl: "videos/Question-Answering/Advanced--Answering-Complex-Questions/index.html"
                    },
                    {
                    title:"Problem Set: Lexical Semantics and Question Answering",
                    type: "ps",
                    contentUrl: "problem-sets/index.html?ps=Lexical-Semantics-And-Question-Answering"
                    }
                ]
                },
                {
                heading: "Summarization",
                members: [
                    {
                    title:"Introduction to Summarization",
                    type: "lecture",
                    contentUrl: "videos/Summarization/Introduction-to-Summarization/index.html"
                    },
                    {
                    title:"Generating Snippets",
                    type: "lecture",
                    contentUrl: "videos/Summarization/Generating-Snippets/index.html"
                    },
                    {
                    title:"Evaluating Summaries: ROUGE",
                    type: "lecture",
                    contentUrl: "videos/Summarization/Evaluating-Summaries--ROUGE/index.html"
                    },
                    {
                    title:"Summarizing Multiple Documents",
                    type: "lecture",
                    contentUrl: "videos/Summarization/Summarizing-Multiple-Documents/index.html"
                    }
                ]
                },
		/*
                {
                heading: "Instructor Chat II",
                members: [
                    {
                    title:"Instructor Chat II",
                    type: "lecture",
                    contentUrl: "videos/Instructor-Chat-II/Instructor-Chat-II/index.html"
                    }
                ]
                }
		*/
            ];
