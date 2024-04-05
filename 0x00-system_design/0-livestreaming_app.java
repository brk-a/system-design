public class VideoConsumingService{
    public DateTime getSeekTime(String userID, String videoID){
        private Database database = new Database();
        WatchedVideo watchedVideo = database.getWatchedVideo(userID, videoID);
        return watchedVideo.getSeekTime();
    }
}

public class Video{
    String Id;
    Frame[] frames;
    Object jsonMetadata;

    public Frame[] getVideoFrames(String userID, String videoID, DateTime next){
        //TO DO: verify user id
        //TO DO: check if video exists

        //initialise frames
        Frame[] frames = [];

        //TO DO: put frames that fit the `next` criteria into `frames`
        // next = endTimestamp + offset

        //return `frames`
        return frames;
    }

    public String getId() {
        return Id;
    }
}

public class Frame{
    byte[] bytes;
    DateTime startTimestamp;
    DateTime endTimestamp;
    int final OFFSET = 10;
}

public class User{
    String Id;
    String name;
    String email;

    public String getId() {
        return Id;
    }
}

public class WatchedVideo {
    String Id;
    String videoId;
    String userId;
    DateTime seekTime;

    public DateTime getSeekTime() {
        //body

        return DateTime seekTime;
    }
}

public class Database {}

public class VideoService {
    private FileSystem fileSystem;

    public Frame getFrame(String userID, String videoID, DateTime next){
        //TO DO: verify user id
        //TO DO: check if video exists

        //initialise video
        Video video = fileSystem.getVideo(videoID);

        //put frame that fits the `next` criteria into `frame`
        // next = endTimestamp + offset
        Frame frame = video.getFrame(next);

        //return `frame`
        return frame;
    }
}

public class FileSystem {
    public Video getVideo(String videoId){
        //body
        return Video video;
    }
}