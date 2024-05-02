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
    - balancer could be a typical one or a distributed queue
    - identifire(s) may appear on ore than one processor host, therefore, said hosts must aggregate their output to a storage host

        ```mermaid
        ---
        title: hash table w. multiple processor hosts
        ---
        flowchart LR
        A[A B C A A D C A B C]-->B[load balancer]
        B-->C[C=2, D=1 A=2, B=1]
        B-->D[C=1, A=2, B=1]
        C-->E[C=3, D=1, A=4, B=2]
        D-->E
        ``` 
    
    - the load balancer increases throughput of the system
    - we, now, must deal with memory constraints on processor hosts and storage host
    - perhaps break data into smaller chunks
    - data passes through data partitioner. data partitioner, well, *partitions* data on the table. partitions are sent to specific processor hosts
    - inside each processor host, create a hash table out of partitioned data. create a list of *top k* using a heap from data in the hash table
    - merge sorted lists (heaps) and store them in the storage host

        ```mermaid
        ---
        title: hash table w. multiple processor hosts and data partitioner
        ---
        flowchart LR
        A[A B E C A F A D C A B C]-->B[data partitioner]
        B-->C[C=3, D=1, B=2]
        B-->D[A=4, E=1, F=1]
        C-->E[A=4, C=3, B=2, E=1]
        D-->E
        ```
    
    - processor host passes a list of size k to storage host
* new problem: unbounded data set; that is, a data set of size N where N approaches &infin;
    - use time as a bound, that is, implement the previous approach on data captured w/i a specified time interval, say, a minute
    - example: list of top k watched videos. capture data for a minute, find top k most watched. store in storage host. perform these ops EMOM
    - say you want to get top k per hour yet you have 60 top k*s* per minute. there's no precise solution, imo; looking for answers too... ::hourglass::
    - we can, however, store the per-minute data on the storage host then apply a batch-process-top-k op on every 60 data sets
* new problem: consistency of data in partitions
    - we, somehow, must replicate data on each partition or ensure consistency otherwise
    - consistency must hold when adding or removing partitions
    - there are solutions, however, they have trade-offs; the most significant is accuracy
    - enter *count-min sketch*...
        - count-min sketch is a data structure. think of it as a 2D array: the width is the pre-defined length of any of the arrays and the height is the number of hash functions in the structure
        - calculate the hash value of incoming data using each function and add one to the corresponding index in the respective array
        - example store A to the count-min sketch: use hash function to calc hash value of A using its identifier. the hash value is an index, *i*, on the array that corresponds to the repective hash functions. there will be N hash values, i<sub>n</sub>, where N is the number of hash functions and 0 &le; n &le; N. use said hash values to add one to the value of A\[i<sub>n</sub>\] in each array
        - there will be collisions; that is alright
        - to retrieve data, take the min value of all counters of A
        - to choose width and height of count-min sketch, you need *d* &rarr; certainity with which we achieve accuracy and *e* &rarr; accuracy we want to have
    - how does count-min sketch apply to our problem? glad you asked...
        - count-min sketch replaces the size-N hash table that receives the stream of data because, unlike the original hash table, count-min sketch is a hash table that grows big without growing big
        - we still need a heap to store the heavy hitters (the top k itema)
        - 

    
    ```mermaid
    ---
    title: high-level architecture
    ---
    flowchart LR
    A((user))--B[API gateway]
    B--C[distributed messaging system]
    C--fast path--D[fast processor count-min sketch]
    C--slow path--E[slow processor]
    D--F[storage processor]
    E--G[distributed messaging system]
    G--H[partition processor]
    H--I[distributed file sys]
    I--J[frequency count mapReduce job]
    J--K[top K map reduce job]
    H--F
    K--F
    F--L[(DB)]
    ```



[def]: ./0-top_k_problem_single_host.java