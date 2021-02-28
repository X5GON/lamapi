#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import datetime
from text2phraser import train_model


# In[2]:


# corpuspath = "../../all_text_transcriptions/"
corpuspath = "../../../predict-series/res/YaleSeriesCorpus"
# directory = os.scandir(corpuspath)
# directory = list(directory)


# In[4]:


texts = []
# for i, file in enumerate(directory[:1]):
#     with open(file.path, "r") as f:
#         avancement = ((i + 1)/len(directory) * 100)
#         if int(avancement) % 10 == 0: print(f"{avancement:.2f} % of file loaded")
#         texts.append("".join(f.readlines()))
    
for root, dirs, files in os.walk(corpuspath):
    for file in files:
        with open(os.path.join(root, file), "r") as f:
#         avancement = ((i + 1)/len(directory) * 100)
#         if int(avancement) % 10 == 0: print(f"{avancement:.2f} % of file loaded")
            texts.append("".join(f.readlines()))
# In[5]:


savedir = f"../../../predict-series/res/YaleSeriesCorpus/phraser_model{datetime.datetime.today().date().isoformat()}"
if not os.path.exists(savedir):
    os.makedirs(savedir)
train_model(texts, savedir)

