# design for a live-streaming system
* the product offers videos to a large number of people on demand
### steps
1. define problems from a user perspective (problems &rarr; features)
    - users should be able to see the videos they select (primary)
        * servers cannot go down (and if they do, there has to be a back-up)
        * bandwidth must be w/i a certain range
        * user must be able to stream a video
        * user must be able to request for a video (search box, etc)
        * user must be able to react to a video (like/dislike, emoji reaction etc)
    - users should be able to choose the resolution of a video (secondary)
        * user must be able to view video in the quality that best suits his/er device
    - users must pay a price for the service
        * user should see ads (app's gotta monetise, innit?)
    - users should be able to see emergency/sensitive broadcasts
        * user must be able to see disclaimers/news flashes
    - etc
2. reduce features to data definitions
    - feature: user should be able to like a video
        * what is a `like` from a data perspective?
            * perhaps an object with
                * `userID` (so we know which user liked the video)
                * `videoID` (so we know which video is liked)
                * `liked` (a boolean that prevents a user from liking more than once)
                * `timestamp` (so we know when video was liked)
                * etc
            * example

                ```typescript
                    interface like = {
                        userID: UUID,
                        videoID: UUID,
                        liked: boolean,
                        timestamp: DateTime,
                        ...
                    }
                ```

    - feature: user should not know how things work in the background
        * client (user app) on the app store
        * client talks to client-facing APIs
        * client-facing API talks to server-facing API
        * server-facing API talks to db
        * reverse process
        * this process should take milliseconds at most
3. define endpoints from which the data in step 2 can be manipulated/queried
    - example: reading comments
        * have an API that facilitates access to comments
        * idea is to have a way to send an electronic signal from the user to the server and back. the `to` signal will be a request and the `from` signal will be a response
4. define your fault tolarance levels
    - you want to make sure none of your services fail when there is an outage
        * best to have servers in different places (in a country/regin or on the globe); this way, an outage is more likely to affect a small geographical region 
        * idea is to have a server on standby just in case an outage occurs
        * there will be duplication of data; this is a necessary evil. alternatively, you can implement a partitioning algo such X% of users go to server A etc
        * more info for fault tolerance in distributed systems [here][def]
5. implement/ account for extensibility
    - extensibility &rarr; a measure of the ability to extend a system and the level of effort required to implement said extension
    - can be through the addition of new functionality or modification of existing functionality
    - idea is to have enhancements w/o impairing existing system functions
6. test the design
    - perform a run using regular and edge cases; emphasis on the latter
        * do not forget capacity estimation
    - repeat steps 1 to 5 until all tests pass
### example: a high-level appproach to a live-streaming app
* customers can use any device to access videos
    - assume `REST`
        * `GET` request to, say, `watch/` endpoint. `getVideoFrame` function w. params `videoID`, `device` and `offset`. response is a `Frame` object (the vid or a part of it)
* customers can comment on a video
    - assume `REST`
        * `POST` request to, say, `{videoID}/comment/` endpoint. `createComment` function w. params `userID`, `videoID`, `comment`. response is a `Comment` object and success message
*  customers require these videos on demand
    - we must store them somewhere (a DB, of course)
    - what kind of DB do we need?
        * we will store `Frame`, `Comment` objects etc
        * comments are easy: a SQL db which has a `comments` table that has the following columns: `id`, `comment`, `userID` (FK), `videoID` (FK)
        * this means that there are `users` and `videos` tables
    - what network protocol(s) do we need?
        * depends on what we are looking at
        * video frames, for example, require continuous updates (many request-response cycles). request contains the user's ID, and the frame requested: `Frame(id, ctx, next)`, for example. use webRTC w. TCP because order (in this case `ctx`) matters
        * video frame server(s) will, almost certainly, be stateful; be aware
        * comments are not as resource-intensive as video frames, therefore, HTTP w. UDP or TCP works
        * comment server(s) will, almost certainly, be configured to be stateless, therefore, the network protocols chosen must be compatible with the server config
    - how do we talk to the server?
        * many DB solutions, e.g. MySQL, Cassandra, Amazon Dynamo DB and PostgreSQL, define how the client must communicate w. DB; this includes the network protocol to use
        * Elasticsearch, for example, implements HTTP
    - which DB solution(s) do we implement?
        * depends; each has trade-offs
        * SQL-like DBs would be quite expensive from a resources (bandwidth, etc) perspective
        * the choice of DB is also affected by the data you have, e.g. HDFS and S3 are great file systems for videos. alternatively, you can use [vimeo][def2]

    ```mermaid
        graph LR;
        A[customers] --> B[client-facing API]
        B[client-facing API] --> C[server-facing API]
        C[server-facing API] --> D[DB]
        D[DB] --> C[server-facing API]
        C[server-facing API] --> B[client-facing API]
        B[client-facing API] --> A[customers]
    ```


* customers need to create live streams of their content
    - have an expensive (high bandwidth, etc), reliable protocol, say, RTMP to capture the video (raw data) and store it in the db
    - recall: customers have different devices, therefore, different resolution capabilities. there has to be a way to make a, say, 8K video viewable in 144p
    - we need a transformation service to, well, transform a video into the desired resolution
        * how does such a service work?
        * glad you asked...
            1. break the input video into, say, 10-second snips/segments
            2. pass the snips into a coversion function as an arg e.g. `convert("snip-0123-abc.xy", 144)`converts *snip-0123-abc.xy* to 144p
        * this method has a name: *map-reduce*; break input into small problems, solve them and return each solution (funny because no *reduce* actually takes place)

            ```mermaid
            graph LR
            A[video] --> B[snip 1]
            A --> C[snip 2]
            A --> |...| D[snip N]
            B --> E[server 1 converts to 1440p]
            C --> F[server 2 converts to 720p]
            D --> G[server N converts to X res]
            B --> F
            B --> G
            C --> E
            C --> G
            D --> E
            D --> F
            E --> H[server N compresses 1440p]
            F --> I[server N-1 compresses 720p]
            G --> J[server 1 compresses X res]
            H --> K[1440p, compressed]
            I --> L[720p, compressed]
            J --> M[X res, compressed]
            ```

* customers need to get the video they ask for
    - how do we get a video from the server to the client?
        * network protocols; network protocols everywhere...
        * webRTC is great for P2P ops e.g. zoom calls
        * MPEG-DASH is great for livestreaming. also, the client can receive said video at whatever resolution his/er device is capable of
        * HLS is, in a way, MPEG-DASH for MacOS and iOS
    - what kind of data do you want to store on the server?
        * do you want to store any data at all?
        * how about the state/statelessness? state*ful* for state*less*?
        * do you need CDNs, caches etc?
        * etc
### example: a low-level appproach to a live-streaming app
* the only thing a customer care about is this: watch the video I request when I request for it
    - the problems to solve, from a sys design perspective, are:
        1. have a way to request a video
        2. have a way to fetch a video
        3. do this in as little time as possible
    - two approaches:
        1. get directly into the code at the start (objects required in the system from a OOP perspective etc)
        2. ask the following: what actions can a user perform? (drag the seek bar to a particular time stamp or press the play button when the video loads, press the pause button etc)
    - emphasis on the second approach
    - idea, from an engineering perspective, is to optimise memory and API calls taking into account user behaviour
        * concurrency, throughput, latency, chunking, caching etc
    - 

[def]: https://www.geeksforgeeks.org/fault-tolerance-in-distributed-system/
[def2]: https://vimeo.com/