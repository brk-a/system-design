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

    - feature: user should know how things work in the background
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
### example
* customers can use any device to access videos
    - assume `REST`
        * `GET` request to, say, `watch/` endpoint. `getVideoFrame` function w. params `videoID`, `device` and `offset`. response is a `Frame` object (the vid or a part of it)
* customers can comment on a video
    - assume `REST`
        * `POST` request to, say, `{videoID}/comment/` endpoint. `comment` function w. params `userID`, `videoID`, `comment`. response is a `Comment` object and success message
*  customers require these videos on demand
    - we must store them somewhere (a DB, of course)
    - what kind of DB do we need?
        * we will store `Frame`, `Comment` objects etc
        * comments are easy: a SQL db which has a `comments` table that has the following columns: `id`, `comment`, `userID` (FK), `videoID` (FK)
        * this means that there are `users` and `videos` tables

    ```mermaid
        graph LR;
        A[customers] --> B[client-facing API]
        B[client-facing API] --> C[server-facing API]
        C[server-facing API] --> D[DB]
        D[DB] --> C[server-facing API]
        C[server-facing API] --> B[client-facing API]
        B[client-facing API] --> A[customers]
    ```

* custo
[def]: https://www.geeksforgeeks.org/fault-tolerance-in-distributed-system/