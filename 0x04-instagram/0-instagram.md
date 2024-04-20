# 0x04-instagram
### features
* store and get images &rarr; see the [tinder sys design][def]
* like and comment on images
* follow a user
* publish a news feed
### like and comment on images
* images are nothing but posts
    - ask yourself: can a user comment on a comment? (how many levels of recursion do you want?)
    - instagram allows replies to comments; does not allow replies to replies (one level of recursion)
    - 

    ```mermaid
    ---
    title: schema for Likes object
    ---
        classDiagram
        Likes : +string Id
        Likes : +string type
        Likes : +string activityID
        Likes : +string userID
        Likes : +DateTime timestamp
        Likes : +Boolean active
    ```

    ```mermaid
    ---
    title: schema for Post object
    ---
        classDiagram
        Post : +string Id
        Post : +string userID
        Post : +string post
        Post : +string imageURL
        Post : +DateTime timestamp
    ```

    ```mermaid
    ---
    title: schema for Comment object
    ---
        classDiagram
        Comment : +string Id
        Comment : +string userID
        Comment : +string postID
        Comment : +string comment
        Comment : +string imageURL
        Comment : +DateTime timestamp
    ```

    ```mermaid
    ---
    title: schema for User object
    ---
        classDiagram
        User + string Id
        User : +string email
        User : +string hashedPassword
    ```

    ```mermaid
    ---
    title: schema for Activity object
    ---
        classDiagram
        Activity : +string Id
        Activity : +int numOfLikes
    ```

### follow a user
* two questions:
    1. who follows you?
    2. who do you follow?
* one table with the following:
    - `follower_id` &rarr; the user id of the follower
    - `followee_id` &rarr; the user id of the followee (one being followed)
    - `timestamp` &rarr; time the following begun
* say user A has id abc-123-xyz. the following query will show all of A's followers

    ```sql
        SELECT follower_id
        FROM follow_table
        WHERE followee_id = "abc-123-xyz";
    ```

* to find out what/who A follows

    ```sql
        SELECT followee_id
        FROM follow_table
        WHERE follower_id = "abc-123-xyz";
    ```

### publish a news feed
* gateway will have the auth, reverse proxy etc required to interface outside comms protocols with internal ones
* user may send a request to gateway using HTTP or XMPP (web sockets) etc
* gateway connects to user feed service (a cluster of servers, typically); there may be load balancers to distribute user requests equitably
* gateway also has a mapping/snapshot of what user feed service boxes are available and where they are located
* the user request uses said mapping to tell the load balancer where it needs to get the relevant box (assume consistent hashing)
* to get a set of what user A follows, a method, say, `getUsersFollowedBy("abc-123-xyz")` will form the `GET` request to the follow service
* to get a set of posts by user A, a method, say, `getPostsByUser("abc-123-xyz")` will form the `GET` request to the posts service
* we can pre-compute the user feed to make the process efficient
    - a user feed is, simply, a set of posts that fit a user's criteria
    - criteria: people/pages/topics a user follows, location, sex etc
    - say user A follows user B: the former's feed must be updated every time the latter posts
    - generally, the posts service must update the user feed service with the latest posts. the user feed service must figure out which posts are relevant to an individual user and avail them
    - the user profile service will ask the follow service for a set of what user A follows. if the `userID` of the post matches with a user id in the set returned by the follow service, then that post can be viewed by user A because user A follows the author of the post
    - iterate over every user in the DB
* use a cache to store pre-computed user feeds for easy and efficient retrieval

    ```mermaid
    ---
    title: sys design for instagram
    ---
    flowchart LR
    A((users))--user 1-->B[gateway/reverse proxy etc 1]
    A--user 2-->C[gateway/reverse proxy etc N]
    A--user 3-->B
    A--user N-->C
    B-->D[user feed service]
    C-->D
    E[posts service]<-->D
    F[follow service]<-->D
    B-->G[(DB)]
    C-->H[(DB)]
    D-->I[(DB)]
    E-->J[(DB)]
    F-->K[(DB)]
    D-.->L[cache]
    ```

### celebrity post fan-out
* what happens when a user that has millions of followers posts?
    - all  the followers will ahve to receive a notification and the post would have to appear on their feeds
    - this will crash the system if we use the current set-up
* two approaches to solve this
    - batch processing: send the notifications and feeds in, well, batches of, say, 1000. you will apply rate limiting etc
    - let the followers pull notifications from the server. each follower pools the server regularly and recives, in their feed, posts from the users they follow
* apply a pull, not a push, model; the former excels at fanning out, the latter is seamless from a UX perspective

[def]: ../0x01-tinder/0-tinder.md