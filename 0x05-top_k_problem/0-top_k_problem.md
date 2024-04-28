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
### approach
* say we have a single host and the data is in a hash table of size N
    - say the data viz: A B C A A D C A B C
    - calculate how many times each unique data element appears in the table
        * A &rarr; 4, B &rarr; 2, C &rarr;  3 and D &rarr; 1
    - we can sort the list in descending order (slow) or we can use the heap approach (faster)
        * whole-list sort: A &rarr; 4, C &rarr;  3, B &rarr; 2 and D &rarr; 1
        * heap sort (say k = 2): A &rarr; 4 and C &rarr;  3
    - the former (sorting the whole list) takes O(Nlog(N)); the latter takes O(Nlog(k)) where k &rarr; the k  in *top k*
    - goes w/o saying that k <= N always; both approaches perform identically when k = N
    - see [this flow][def]

        ```mermaid
        ---
        title: data structures to use
        ---

        classDiagram
        HeavyHitter : +String identifier
        HeavyHitter : +int frequency
        ```

* how do we approach the problem when #hosts > 1?
    - perform calculations in parallel, trivially
    - perhaps a load balancer...

[def]: ./0-top_k_problem_single_host.java