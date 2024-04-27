# top k problem
* design a sys that identifies the top k items in a set
    - top 10 songs on your play list
    - top 11 searches on your search engine
    - top N trends on your favourite social media
    - etc
* clearly, a DB and/or distributed cache will not solve the problem
* `MapReduce`, by itself, is not sufficient to solve the problem
### functional requirements
* a function, `topK(k, startTime, endTime)`, that returns the top `k` items in a set within the closed interval bound by `startTime` and `stopTime`
### non-fuctional requirements
* scalable &rarr; scales directly proportionally to the amount of data
* highly available &rarr; survives HW/SW failures, also, no single point of failure
* highly performant &rarr; takes tens of milliseconds to return 100 items
* accuracy &rarr; this list changes with time; we should aim for the most recent one
