# notification system
* design a notification system
### the problem
* web services send messages in reaction to an event
* examples
    - notify a card holder when transaction amount exceeds transaction limit
    - notify  the on-call engineer when service monitoring system encounters a large amount of faults produced by an API
* generally: say there is a service, P, called Publisher that produces messages which must be delivered to a group of other services, S, called Subscribers. we can set up synchronous communication between P and S such that P calls each S in some order and awaits a response. Bad idea. this introduces a number of challenges: it is difficult to scale when S &rarr; &infin; and/or #messages &rarr; &infin;. also, it is difficult to extend such a solution to support different types of S
* what if we had a system that register an arbitrarily large number of Ps and Ss, coordinate message delivery between them, be fault tolerant and be scalable; this system is the notification system we must build

    ```mermaid
    ---
    title: notification system concept
    ---
        %%{init: {"flowchart": {"htmlLabels": true}} }%%
        flowchart LR
        A[P]-->B[notification service]
        B-->C["`S<sub>1</sub>`"]
        B-->D["`S<sub>2</sub>`"]
        B-->E["`S<sub>N</sub>`"]
    ```

#### functional requirements
* create three APIs
    - `createTopic(topicName)` &rarr; creates a new topic
    - `publish(topicName, message)` &rarr; publishes a message to a topic
    - `subscribe(topicName, endpoint)` &rarr; allows S to receive messages from a topic
    - a topic is a named resource to which messages are sent; think of it as a bucket that stores messages from a publisher. all S receive a copy of the message from the bucket
#### non-functional requirements
* scalable &rarr; supports an arbitrarily large number of topics, Ps and Ss
* available &rarr; survives hardware/network failures; no single point of failure
* performant &rarr; keeps end-to-end latency as low as possible
* durable &rarr; messages must not be lost; each S must get each message at least once