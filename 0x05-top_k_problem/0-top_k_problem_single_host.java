class HeavyHitter {
    public final String identifier;
    public final int frequency;

    public HeavyHitter(String identifier, int frequency){
        this.identifier = identifier;
        this.frequency = frequency;
    }
}

public List<HeavyHitter> topK(String[] events, int k){
    Map<String, Integer> frequencyTable = new HashMap<String, Integer>();
    for(String event: events)
        frequencyTable.put(event, frequencyTable.getOrDefault(event, 0)+1);
    
    PriorityQueue<HeavyHitter> heap;
    heap = new PriorityQueue<HeavyHitter>(Comparator.comparing(e -> e.getFreQuency()));
    for(Map.Entry<String, Integer> entry: frequencyTable.entrySet()){
        heap.offer(new HeavyHitter(entry.getKey(), entry.getValue()))

        if(heap.size()>k)
            heap.poll();
    }

    List<HeavyHitter> result = new ArrayList<HeavyHitter>();
    while(heap.size()>0)
        result.add(heap.poll());
    
    return result;

}