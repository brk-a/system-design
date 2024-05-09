public class TokenBucket {
    private final long maxBucketSize;
    private final long refillRate;
    private double currentBucketSize;
    private long lastRefillTimestamp;

    public TokenBucket(long maxBucketSize, long refillRate){
        this.maxBucketSize = maxBucketSize;
        this.refillRate = refillRate;

        currentBucketSize = maxBucketSize; // #tokens is, initially, = max cap
        lastRefillTimestamp = System.nanoTime();
    }

    public synchronized boolean allowRequest(int tokens){ // sync because several methods may call `allowRequest` concurrently
        refill(); //refill bucket w. tokens accumulated since last call

        if(currentBucketSize>tokens){ //call is allowed if bucket has enough tokens
            currentBucketSize -= tokens;
            return true;
        }

        return false; //call is throttled because bucket does not have enough tokens
    }

    private void refill(){
        long now = System.nanoTime(); //current time in ns
        double tokensToAdd = (now - lastRefillTimestamp) * refillRate / 1e9; // this is the #tokens accumulated since last refill
        currentBucketSize = Math.min(currentBucketSize+tokensToAdd, maxBucketSize); // #tokens <= max cap always
        lastRefillTimestamp = now;
    }
}