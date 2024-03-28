# design for a live-streaming system
* the product offers videos to a large numbe rof people on demand
### steps
1. define problems from a user perspective (problems &rarr; features)
    - users should be able to see the videos they select (primary)
        * servers cannot go down (and if they do, there has to be a back-up)
        * bandwidth must be w/i a certain range
    - users should be able to choose the resolution of a video (secondary)
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

3. define endpoints from which the data in step 2 can be manipulated/queried
    - example: reading comments
        * have an API that facilitates access to comments
        * idea is to have a way to send an electronic signal from the user to the server and back. the `to` signal will be a request and the `from` signal will be a response
4. 