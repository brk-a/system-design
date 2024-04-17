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


[def]: ../0x01-tinder/0-tinder.md