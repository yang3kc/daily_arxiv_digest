# arXiv digest — 2026-07-15

- Fetched 119 papers from cs.CY, cs.CL
- Selected 33 papers (relevance ≥ 0.8)
- Model: gpt-4.1-mini (openai)

## Security of AI and language models (3 papers)

### [From Prompt Risk to Response Risk: Paired Analysis of Safety Behavior of Large Language Models](https://arxiv.org/abs/2604.26052)

Mengya Hu, Qiong Wei, Sandeep Atluri

**TL;DR:** This paper analyzes how large language models handle harmful prompts by comparing the risk level of the input prompt to the model's response across different harm categories. The study finds that most responses reduce harm, some maintain the same level, and a small portion escalate harm, often due to either adding unwanted harmful details or matching the prompt's severity. The research also highlights a tradeoff between helpfulness and safety, with safer responses tending to be less relevant, and provides publicly available tools and data for further evaluation.

**Relevance 0.90** — The paper focuses on safety evaluations of large language models, analyzing harmful content and risk escalation, which is directly related to security concerns in AI.

### [A Threshold Exceedance Framework for CBRN Uplift Evaluation in Frontier Language Models](https://arxiv.org/abs/2607.12200)

Rahul Gupta, Abhinav Mohanty, Payal Motwani, Venkatesh Saligrama, Satyapriya Krishna, Connor Harris, Gary Anthony Ackerman, Brandon Behlendorf, Tom Hobson, Theodore Wilson, ...

**TL;DR:** This paper presents a new framework to evaluate how much advanced language models help non-experts plan dangerous chemical, biological, radiological, or nuclear attacks compared to public tools. The authors conducted a large study where experts reviewed attack plans created or improved with model assistance, finding that significant risk increase was mainly seen in radiological scenarios. Their approach offers clear guidelines for future assessments to better inform safety and policy decisions.

**Relevance 0.90** — The paper focuses on evaluating the risk of language models increasing the ability to plan CBRN misuse, which is directly related to security concerns of AI.

### [A Neurosymbolic Approach to Natural Language Formalization and Verification](https://arxiv.org/abs/2511.09008)

Chenyang An, Sam Bayless, Stefano Buliani, Darion Cassel, Byron Cook, Duncan Clough, R\'emi Delmas, Nafi Diallo, Ferhat Erata, Nick Feng, ...

**TL;DR:** This paper presents ARc, a system that combines large language models with human input to convert natural language policies into formal logic, enabling precise verification of statements against these policies. By performing multiple checks to ensure consistency, ARc achieves over 99% accuracy and almost no false positives in validating logical correctness. This approach provides transparent, auditable results and is the first commercial tool from a major cloud provider to integrate automated reasoning as a safety measure in AI applications.

**Relevance 0.80** — The paper discusses formal correctness guarantees and automated reasoning checks to ensure logical validity, which relates to security and reliability of AI systems.

## Applications of AI and language models in social science research (8 papers)

### [So Many Opinions, So Many LLMs: Comparing Large Language Models to Traditional Machine Learning for Open- Ended Survey Analysis](https://arxiv.org/abs/2607.11890)

Abdullah Akinde, Mariam Akinde, Rasheedat Emiola, Ahmed Akinsola

**TL;DR:** This study compares advanced large language models (LLMs) like GPT and LLaMA to traditional machine learning methods for analyzing open-ended survey responses. It finds that LLMs generally provide more accurate classification of sentiments and themes but vary in how clearly they explain their decisions. The research highlights a trade-off between improved accuracy and challenges in consistency and interpretability when using LLMs for qualitative survey analysis.

**Relevance 1.00** — The paper directly discusses using large language models to analyze open-ended survey data, which is a social science research application.

### [AgentSociety 2: An Integrated Research Environment for Executable Social Science](https://arxiv.org/abs/2607.11895)

Jinghua Piao, Jun Zhang, Haoyu Huang, Keming Zhang, Jing Yi Wang, Songwei Li, Boyuan Sun, Jiayi Chang, Fengli Xu, Chunyan Wang, ...

**TL;DR:** This paper presents AgentSociety 2, a system that integrates AI agents to both conduct social science research and simulate participant behaviors within social environments. By combining hypothesis generation, experiment design, and simulation in one platform, it enables comprehensive and auditable social science workflows. The system successfully replicates known social patterns and supports large-scale simulations, offering a powerful tool for advancing computational social science with human oversight.

**Relevance 1.00** — The paper presents AgentSociety 2, an integrated research environment that uses AI and language models specifically for executable social science research, including hypothesis generation, experiment design, and simulation execution.

### [Does Topic Sentiment Cause Perceived Ideology? Comparing Human and LLM Annotations in Political News Articles](https://arxiv.org/abs/2606.06715)

Upasana Chatterjee

**TL;DR:** This paper investigates whether the sentiment expressed on specific topics influences how people perceive political ideology, comparing labels assigned by humans and large language models (LLMs). Using advanced statistical methods on political news articles, the study finds that LLMs without fine-tuning tend to exaggerate the effect sizes, while fine-tuning brings their assessments closer to human judgments. The findings suggest that while LLMs can detect the presence and direction of ideological effects, they may misestimate their strength, affecting their reliability as substitutes for human annotations in causal analyses.

**Relevance 0.90** — The paper studies the causal effect of topic sentiment on perceived political ideology using AI language models and human annotations, which is a direct application of AI in social science research.

### [From Sentiment to Actionable Insights: Public Sentiment Analysis of Advanced Air Mobility](https://arxiv.org/abs/2606.20751)

Esrat Farhana Dulia, Amina Dhaher, Raiful Hasan, Syed Arbab Mohd Shihab

**TL;DR:** This study analyzes over 300,000 public comments from Reddit and Quora to understand people's feelings about advanced air mobility (AAM) using various AI sentiment analysis methods, finding that ModernBERT works best. It then identifies key topics like safety, regulations, and noise concerns that shape public opinion. These insights can guide policymakers and industry leaders in addressing public worries and promoting the safe and accepted use of AAM technologies.

**Relevance 0.90** — The paper applies AI and language models to analyze public sentiment and discourse on Advanced Air Mobility, which is a social science research application.

### [Fine-Tuned Multi-Agent Framework for Detecting OCEAN in Life Narratives](https://arxiv.org/abs/2607.12215)

Rasiq Hussain, Darshil Italiya, Joshua Oltmanns, Mehak Gupta

**TL;DR:** The paper introduces a new method that uses multiple specialized AI agents to better detect personality traits from long life stories. Each agent focuses on different trait perspectives, and a judge model combines their insights to improve accuracy and reduce bias. This approach outperforms single-model methods and provides clearer, more reliable personality assessments from text.

**Relevance 0.90** — The paper focuses on detecting OCEAN personality traits from life narratives using AI, which is a direct application of AI in social science research, specifically personality psychology.

### [Can Induced Emotion Bias LLM Behaviors in Sequential Decision Making?](https://arxiv.org/abs/2607.12631)

Minh Khoi Ho, Zihao Zhu, Runchuan Zhu, Levina Li, Zhiwen Fan, Zhangyang Wang, Junyuan Hong

**TL;DR:** This study explores whether emotions induced in large language models (LLMs) affect their decision-making in uncertain situations, using a psychological task called the Iowa Gambling Task. The researchers found that while LLMs can recognize emotions and learn from interactions, induced emotions generally do not bias their decisions like they do in humans. However, when anger is induced, LLMs become less sensitive to negative outcomes and tend to explore fewer options early on, showing a unique emotional influence on their behavior.

**Relevance 0.80** — The paper uses LLMs to study decision-making under uncertainty and emotion induction, which relates to social science research methods.

### [Modeling Story Expectations: A Generative Framework using LLMs](https://arxiv.org/abs/2412.15239)

Hortense Fong, George Gui, Bo Yang

**TL;DR:** This paper presents a new method that uses large language models to predict what readers expect to happen next in stories by generating possible continuations and analyzing features like emotions and plot paths. The approach was validated by comparing these predictions to both human survey responses and actual story outcomes, showing strong alignment. The findings reveal that these forward-looking expectations help explain reader engagement beyond just the story content already seen.

**Relevance 0.80** — The paper applies large language models to model consumer expectations and engagement with stories, which is a social science research application.

### [FairCoder: Probing LLM Bias in High-Stakes Decision Making via Coding Tasks](https://arxiv.org/abs/2501.05396)

Yongkang Du, Jen-tse Huang, Jieyu Zhao, Lu Lin

**TL;DR:** This paper introduces FairCoder, a new way to test biases in large language models by having them perform coding tasks related to important decisions like hiring and college admissions. The authors also propose FairScore, a metric that measures both how often models refuse biased requests and how outcomes differ across groups. Their experiments reveal hidden biases, such as favoring applicants from wealthy families, highlighting risks in using these models for critical decisions.

**Relevance 0.80** — The paper applies LLMs to social domains like hiring, education, and healthcare, which are key areas in social science research.

## Using AI to simulate humans in various contexts (5 papers)

### [AgentSociety 2: An Integrated Research Environment for Executable Social Science](https://arxiv.org/abs/2607.11895)

Jinghua Piao, Jun Zhang, Haoyu Huang, Keming Zhang, Jing Yi Wang, Songwei Li, Boyuan Sun, Jiayi Chang, Fengli Xu, Chunyan Wang, ...

**TL;DR:** This paper presents AgentSociety 2, a system that integrates AI agents to both conduct social science research and simulate participant behaviors within social environments. By combining hypothesis generation, experiment design, and simulation in one platform, it enables comprehensive and auditable social science workflows. The system successfully replicates known social patterns and supports large-scale simulations, offering a powerful tool for advancing computational social science with human oversight.

**Relevance 1.00** — The paper describes silicon participants that generate behavioral responses within configurable social environments, effectively simulating human behavior in social science experiments.

### [CityBehavEx: A Scalable and Empirically Validated LLM-Assisted Urban Simulation Platform](https://arxiv.org/abs/2607.12086)

Gustavo H. Santos, Aline Viana, Thiago H Silva

**TL;DR:** This paper introduces CityBehavEx, a new urban simulation platform that uses a combination of human mobility models and fine-tuned language models to efficiently simulate realistic city-scale human behaviors. The platform can simulate large populations quickly while allowing users to inspect and validate agent behaviors against real-world data. Their approach produces mobility patterns that closely match actual spatial, temporal, and activity distributions, demonstrating improved scalability and accuracy over previous methods.

**Relevance 1.00** — The paper presents a platform that uses LLMs and mobility models to simulate city-scale human behavior and routines, directly involving AI-based human simulation.

### [Comparing Semantic Navigation in Humans and Large Language Models using Natural Language Processing](https://arxiv.org/abs/2607.12195)

Gabriel Paris-Colombo, Rodrigo M. Cabral-Carvalho, Felipe D. Toro-Hern\'andez

**TL;DR:** This study compared how humans and advanced language models search through semantic memory by analyzing verbal fluency tasks. Using trajectory-based metrics, the researchers found that humans explore concepts more variably and broadly than the models, which showed more predictable and narrower search patterns. Adjusting model settings only partially matched human behavior, indicating current models don't fully capture the balance of exploration and exploitation seen in human semantic search.

**Relevance 0.90** — The paper directly compares human semantic search behavior with that of large language models, effectively using AI to simulate and understand human cognitive processes.

### [Can Induced Emotion Bias LLM Behaviors in Sequential Decision Making?](https://arxiv.org/abs/2607.12631)

Minh Khoi Ho, Zihao Zhu, Runchuan Zhu, Levina Li, Zhiwen Fan, Zhangyang Wang, Junyuan Hong

**TL;DR:** This study explores whether emotions induced in large language models (LLMs) affect their decision-making in uncertain situations, using a psychological task called the Iowa Gambling Task. The researchers found that while LLMs can recognize emotions and learn from interactions, induced emotions generally do not bias their decisions like they do in humans. However, when anger is induced, LLMs become less sensitive to negative outcomes and tend to explore fewer options early on, showing a unique emotional influence on their behavior.

**Relevance 0.90** — The paper investigates LLMs simulating human-like decision-making and emotional responses in a psychological task.

### [When Does Personality Composition Matter for Multi-Agent LLM Teams?](https://arxiv.org/abs/2606.27443)

Aryan Keluskar, Amrita Bhattacharjee, Huan Liu

**TL;DR:** This paper studies how changing the personality traits of large language model agents affects their teamwork on different tasks. By adjusting traits like agreeableness, the authors tested teams on coding, research collaboration, and bargaining tasks. They found that personality changes impact performance differently depending on the task, with little effect on coding but significant effects on collaboration and bargaining outcomes.

**Relevance 0.80** — The paper manipulates personality traits in LLM agents to study communication and team performance, which involves simulating human-like personalities and interactions.

## Methods to increase the factuality of language model response (7 papers)

### [Evidence-Grounded Verified Agentic Reasoning: A Path Toward Eliminating LLM Hallucination in Empirical Inference via Tool-Attested Kernel Proofs](https://arxiv.org/abs/2607.12650)

Junyu Ren

**TL;DR:** This paper introduces EG-VAR, a system that ensures large language model (LLM) outputs are backed by verified evidence and formal reasoning, reducing hallucinations in empirical inference. By integrating a formal proof kernel with tool calls, EG-VAR guarantees that every verified claim is traceable and logically sound, achieving perfect accuracy on tested numerical reasoning tasks and maintaining source fidelity under stress tests. The approach also provides transparent audit trails and explicit handling of uncertainties, paving the way for trustworthy AI in high-stakes decision-making.

**Relevance 1.00** — The paper focuses on eliminating hallucination in LLMs and ensuring verified, evidence-grounded reasoning, directly addressing factuality.

### [On-Device Deep Research at 4B: Exposure Bounds Faithfulness, Retrieval Bounds Coverage](https://arxiv.org/abs/2607.12257)

Vinay Kumar Chaganti

**TL;DR:** This study evaluates how well a small on-device AI model can produce faithful citations when summarizing research papers on a personal laptop. By varying how much of each source the model reads and the quality of those sources, the researchers found that reading more of each source improves citation faithfulness, while the ability to cite the right sources depends on retrieval quality. The key takeaway is to first increase the amount of source content the model processes to boost faithfulness, then focus on improving retrieval to enhance coverage.

**Relevance 0.90** — The paper studies factors affecting the faithfulness of citations generated by a language model, which relates directly to improving factuality of model responses.

### [Knowledgeless Language Models: Suppressing Parametric Recall for Evidence-Grounded Language Modeling](https://arxiv.org/abs/2607.12831)

Roi Cohen, Yvan Carr\'e, Nick Lechtenb\"orger, Hendrik Droste, Lucas Kerschke, Russa Biswas, Gerard de Melo, Jan Buys

**TL;DR:** This paper introduces a new training approach for language models that removes direct factual knowledge by anonymizing named entities during pretraining. This method reduces the model's reliance on memorized facts and encourages it to depend more on provided evidence, leading to better performance and reliability in tasks like question answering and fact verification. The resulting models are more robust and calibrated, especially when dealing with imperfect or external information sources.

**Relevance 0.90** — The paper focuses on reducing parametric recall and improving evidence-grounded reasoning, which directly relates to increasing the factuality and reliability of language model responses.

### [Can a Language Model Learn Facts Continually in Its Weights?](https://arxiv.org/abs/2607.11020)

Charles O'Neill

**TL;DR:** This paper investigates whether language models can continually learn and retain new facts by updating their internal weights. By testing models with sequences of fact updates, the study finds that while diverse training data helps facts stick better, most newly learned facts are eventually forgotten or redirected by later updates. The authors conclude that relying on the model's context (prompts) is more reliable for maintaining knowledge over time than trying to store facts permanently in the model's weights.

**Relevance 0.80** — The paper studies how language models can continually learn and retain factual knowledge in their weights, which relates to improving the factual accuracy and knowledge retention of language model responses.

### [Scaling Point-in-Time Language Models](https://arxiv.org/abs/2607.11889)

Bryan Kelly, Semyon Malamud, Johannes Schwab, Teng Andrea Xu

**TL;DR:** The paper addresses the problem of lookahead bias in language models caused by training on future data, which affects applications in finance and social sciences. By training large transformer models only on data available up to each point in time, the authors create "point-in-time" models that reduce this bias. Their approach, using up to 4 billion parameters and a trillion tokens, narrows the performance gap with standard models and provides tools for reproducible, temporally valid language modeling.

**Relevance 0.80** — The paper focuses on training language models on temporally filtered data to avoid future information leakage, which directly relates to improving the factuality and temporal validity of model responses.

### [CANDI: Contextual Alignment for Niche Domains Question Answering](https://arxiv.org/abs/2607.11891)

Megha Chakraborty, Darssan L. Eswaramoorthi, Het Riteshkumar Shah, Madhur Thareja, Michelle A Ihetu, Harshul Raj Surana, Kaushik Roy, Amit Sheth

**TL;DR:** This paper introduces CANDI-QA, a new dataset designed to test how well large language models can provide accurate and context-aware answers in specialized fields like medicine and finance. The authors evaluate various language models using this dataset and propose MTSS-Net, a hybrid system combining neural retrieval with rule-based reasoning. Their results show that current models struggle with context alignment in niche domains, highlighting the need for improved methods that integrate contextual and symbolic understanding.

**Relevance 0.80** — The paper focuses on evaluating and improving language models' ability to provide accurate, context-sensitive, and user-aligned answers, which relates to increasing factuality in responses.

### [Evaluating Large Language Models on Misconceptions in Multi-Turn Medical Conversations](https://arxiv.org/abs/2607.12884)

Monica Munnangi, Saiph Savage

**TL;DR:** This paper introduces a new dataset of multi-turn medical conversations to test how well large language models (LLMs) can identify and correct patient misconceptions over multiple exchanges. The study finds that while top models like GPT-5 and Claude-Haiku perform well initially, their ability to correct false beliefs drops significantly in follow-up turns, leading to inconsistent and potentially unsafe advice. The results highlight the challenge of maintaining accurate medical guidance in ongoing dialogues and the need for better evaluation methods.

**Relevance 0.80** — The paper evaluates large language models on their ability to detect and correct misconceptions in multi-turn medical conversations, which relates to improving the factual accuracy and reliability of model responses.

## AI and language models for generating misinformation or fact-checking (4 papers)

### [Evaluating Health Misinformation in Low-Resource Languages: Integrating Small Language Models with a Culturally-Sensitive Responsible NLP Framework (Bangla as a Case Study)](https://arxiv.org/abs/2607.12336)

Farnaz Farid, Raihan Alam, Al Al-Areqi, Farhad Ahamed, Muhammad Hassan Khan, Sadia Hossain, Irena Veljanova, Anika Tabassum Binte Hossain

**TL;DR:** This paper tackles the challenge of detecting health misinformation in low-resource languages like Bangla by using small language models (SLMs) instead of large, costly models. The authors found that the Phi-4 model performed best in identifying false claims and developed a culturally sensitive framework to better evaluate misinformation's impact. Their approach helps improve trustworthy health information access for diverse communities with limited data resources.

**Relevance 1.00** — The paper directly addresses health misinformation detection using AI and language models, including fact-checking aspects.

### [Evidence-Grounded Verified Agentic Reasoning: A Path Toward Eliminating LLM Hallucination in Empirical Inference via Tool-Attested Kernel Proofs](https://arxiv.org/abs/2607.12650)

Junyu Ren

**TL;DR:** This paper introduces EG-VAR, a system that ensures large language model (LLM) outputs are backed by verified evidence and formal reasoning, reducing hallucinations in empirical inference. By integrating a formal proof kernel with tool calls, EG-VAR guarantees that every verified claim is traceable and logically sound, achieving perfect accuracy on tested numerical reasoning tasks and maintaining source fidelity under stress tests. The approach also provides transparent audit trails and explicit handling of uncertainties, paving the way for trustworthy AI in high-stakes decision-making.

**Relevance 0.80** — The paper aims to eliminate unsupported outputs and improve source-faithfulness, which relates to fact-checking and reducing misinformation.

### [Graph-Based Detection of Disinformation Narrative Diffusion between Russian and Ukrainian Telegram Channels](https://arxiv.org/abs/2607.11894)

Yuliia Vistak, Viktoriia Makovska, Vera Schmitt, Veronika Solopova

**TL;DR:** The paper introduces a new method that uses graph analysis and weak supervision to detect and study disinformation stories spreading on Telegram channels. By grouping related claims into narratives and tracking how they spread across channels, the approach uncovers coordinated efforts to amplify false information. This combined use of text and network data offers a scalable way to identify and understand disinformation campaigns in large messaging platforms.

**Relevance 0.80** — The paper focuses on detecting disinformation narratives using AI, which relates to fact-checking and misinformation detection.

### [Beyond Binary Detection: A Multi-Dimensional Taxonomy of Cancer Misinformation on Reddit](https://arxiv.org/abs/2607.12383)

Aria Pessianzadeh, Pooriya Jamie, Naima Sultana, Georgia Himmelstein, Yuliya Zektser, Patricia Ganz, Homa Hosseinmardi, Amir Ghasemian, Rezvaneh Rezapour

**TL;DR:** This paper develops a detailed system to classify different types of cancer misinformation found in Reddit discussions about breast, lung, colon, and prostate cancers. By using expert-labeled data and testing large language models, the study finds that about 6% of these discussions contain misinformation, which varies by community and topic. The research highlights common false claims related to unproven treatments, distrust in conventional medicine, and misleading information about diagnosis and screening.

**Relevance 0.80** — The paper uses language models to detect and classify cancer misinformation, which relates to fact-checking and misinformation detection.

## Methods and applications of using AI for image and video analysis (3 papers)

### [Benchmarking Nighttime Traffic Sign Recognition with Illumination-Adaptive Detection and Semantic Attribute Reasoning](https://arxiv.org/abs/2511.17183)

Aditya Mishra, Akshay Agarwal, Haroon Lone

**TL;DR:** This paper introduces INTSD, a large dataset of nighttime traffic sign images from India, addressing the lack of real-world low-light data for traffic sign recognition. The authors propose LENS-Net, a model combining adaptive illumination detection with semantic reasoning to improve recognition in challenging night conditions. Their experiments show that training with INTSD significantly improves performance over models trained only on daytime data, highlighting the importance of nighttime-specific datasets.

**Relevance 0.90** — The paper focuses on nighttime traffic sign recognition using image data and proposes a dataset and models for detection and classification, which is directly related to AI methods for image analysis.

### [An Empirical Analysis of Continual Learning for Heterogeneous Medical Visual Question Answering](https://arxiv.org/abs/2607.12048)

Mai A. Shaaban, Tausifa Jan Saleem, Alaa Mohamed, Dilnaz Utemissova, Ufaq Khan, Mohammad Yaqub

**TL;DR:** This paper evaluates how well continual learning methods help medical visual question answering models adapt to various clinical tasks without forgetting previous knowledge. The study tests different tasks like classification and report generation, examining how task order affects learning and how model parameters change over time. The main finding is that current continual learning approaches struggle to balance learning new tasks and retaining old knowledge when tasks are diverse and mixed.

**Relevance 0.80** — The paper focuses on medical visual question answering, which involves image analysis combined with language models, specifically in medical imaging contexts.

### [Do We Really Need Multimodal Emotion Language Models Larger Than 1B Parameters?](https://arxiv.org/abs/2607.12787)

Kaiwen Zheng, Junchen Fu, Wenhao Deng, Hu Han, Joemon M. Jose, Xuri Ge

**TL;DR:** This paper introduces Light-MER, a lightweight multimodal emotion recognition model under 1 billion parameters that uses knowledge distillation from larger models to maintain high accuracy. It employs novel optimization techniques to improve knowledge transfer and balance performance with efficiency. Experiments show Light-MER achieves state-of-the-art results while being faster and more suitable for deployment on devices with limited resources.

**Relevance 0.80** — The paper focuses on multimodal emotion recognition involving video, audio, and language, which relates to image and video analysis methods and applications.

## AI as information curation tools such as search engines, news aggregators, etc. (7 papers)

### [Lost in the Maze: Overcoming Context Limitations in Long-Horizon Agentic Search](https://arxiv.org/abs/2510.18939)

Howard Yen, Yoonsang Lee, Ashwin Paranjape, Mengzhou Xia, Thejas Venkatesh, Jack Hessel, Danqi Chen, Yuhao Zhang

**TL;DR:** This paper addresses the challenge of long-horizon agentic search, where existing methods struggle due to context limitations and inefficiencies. The authors propose SLIM, a framework that separates search and browsing tasks and summarizes information periodically to keep context manageable. SLIM outperforms existing open-source systems in accuracy and efficiency, reducing errors and resource use in complex, multi-step web exploration tasks.

**Relevance 0.90** — The paper focuses on agentic search frameworks and information management for long-horizon search tasks, which is directly related to AI as information curation tools.

### [On-Device Deep Research at 4B: Exposure Bounds Faithfulness, Retrieval Bounds Coverage](https://arxiv.org/abs/2607.12257)

Vinay Kumar Chaganti

**TL;DR:** This study evaluates how well a small on-device AI model can produce faithful citations when summarizing research papers on a personal laptop. By varying how much of each source the model reads and the quality of those sources, the researchers found that reading more of each source improves citation faithfulness, while the ability to cite the right sources depends on retrieval quality. The key takeaway is to first increase the amount of source content the model processes to boost faithfulness, then focus on improving retrieval to enhance coverage.

**Relevance 0.80** — The paper discusses on-device research agents that search corpora and cite sources, which relates to AI as information curation tools.

### [Predict the Retrieval! Test time adaptation for Retrieval Augmented Generation](https://arxiv.org/abs/2601.11443)

Xin Sun, Zhongqi Chen, Qiang Liu, Shu Wu, Bowen Song, Weiqiang Wang, Zilei Wang, Liang Wang

**TL;DR:** This paper introduces a method called TTARAG that improves question-answering models by updating them during testing to better handle specialized topics. The approach involves the model learning to predict the information it retrieves, allowing it to adjust itself to new domains on the fly. Experiments show that TTARAG significantly boosts performance compared to standard retrieval-augmented models across various specialized fields.

**Relevance 0.80** — The paper discusses Retrieval-Augmented Generation, which involves retrieving external knowledge to augment language model generation, closely related to AI as information curation tools.

### [FAIR GraphRAG: A Retrieval-Augmented Generation Approach for Semantic Data Analysis](https://arxiv.org/abs/2607.11464)

Marlena Fl\"uh, Soo-Yon Kim, Carolin Victoria Schneider, Sandra Geisler

**TL;DR:** This paper presents a new method that improves how large language models answer complex, domain-specific questions by organizing data into FAIR Digital Objects within a graph structure. By combining these FAIR principles with graph-based retrieval and AI, the approach enhances accuracy, coverage, and explainability, especially in biomedical data analysis. The method was tested on RNA-sequencing data in gastroenterology, showing promising results and potential for use in other specialized fields.

**Relevance 0.80** — The paper presents a graph-based retrieval system integrating FAIR Digital Objects to improve information retrieval and question answering, which relates to AI as information curation tools.

### [Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking](https://arxiv.org/abs/2607.11933)

Shreeya Dasa Lakshminath, Shubhan S

**TL;DR:** The paper presents a method to make large language models more efficient for reranking in retrieval-augmented generation tasks by fine-tuning LLaMA 3 with a two-stage process and applying 4-bit quantization. This approach significantly improves answer quality metrics while reducing computational costs compared to traditional cross-encoders. The results show that instruction-tuned LLMs can serve as accurate and faster rerankers without the usual heavy inference overhead.

**Relevance 0.80** — The paper focuses on improving reranking in Retrieval-Augmented Generation pipelines, which are related to information retrieval and curation, making it relevant to AI as information curation tools.

### [LakeQuest: A Three-Domain Benchmark for Grounded Question Answering across Data Lakes](https://arxiv.org/abs/2607.12310)

Michael Solodko, Steven Gong, Guangwei Yu, Satya Krishna Gorti, Jesse C. Cresswell, Victor Zhong

**TL;DR:** This paper introduces LakeQuest, a new benchmark with nearly 10,000 question-answer pairs designed to test how well QA systems can find and combine information from messy, real-world data lakes across three different fields. The benchmark highlights that even when retrieval is good, current systems often fail at reasoning tasks like linking related data and understanding complex policies. This shows a need for better methods that can accurately discover and integrate information from diverse and unstructured sources.

**Relevance 0.80** — The paper focuses on QA systems that retrieve and synthesize information from heterogeneous data lakes, which is closely related to AI as information curation tools.

### [QUBO-Optimized Evidence Selection for Retrieval-Augmented Question Answering with Unconventional Solvers](https://arxiv.org/abs/2607.12334)

Rahul Singh, Madhav Vadlamani

**TL;DR:** This paper introduces a new method for selecting evidence passages in question answering by formulating the task as a Quadratic Unconstrained Binary Optimization (QUBO) problem. Their approach balances multiple factors like relevance and coverage to choose compact, complementary evidence sets without relying heavily on large language models (LLMs) for selection. Experiments show that this method performs competitively with LLM-based selectors while enabling more efficient and structured evidence selection.

**Relevance 0.80** — The paper focuses on evidence selection for retrieval-augmented question answering, which is a form of information curation and retrieval.
