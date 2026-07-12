there are 2 types of VectoreDatabase : 
- Engine based database (need to install engine in order to work)
- file base data base  (after closing the app the sotred file will be stored as a file on the disk(no url as we use in mongo))
-  Qdrant is file base BD and in the intializaition we get a url , this url is not for an engine its used just for docker so do not get scamed by the url.
- in the file "Qdrant DB" why do we iterate through the metadata eventho it equals to none: 
[text](https://chatgpt.com/c/6a53a2ed-32cc-83ea-aa8d-251f612920d2)