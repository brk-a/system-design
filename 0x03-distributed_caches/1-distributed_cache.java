class Node {
    private final String key;
    private String value;

    private Node prev;
    private Node next;

    public Node(String key, String value) {
        this.key = key;
        this.value = value;
    }

    private String getKey() {
        return key;
    }
    private String getValue() {
        return value;
    }
}

class LRUCache {
    private final Map<String, Node> map;
    private final int capacity;

    private Node head = null;
    private Node tail = null;

    public LRUCache(int capacity) {
        this.map = new HashMap<String, Node>();
        this.capacity = capacity;
    }

    public String get(String key) {
        if(!map.containsKey(key))
            return null;
        
        Node node = map.get(key);

        deleteFromList(node);
        setListHead(node);

        return node.getValue();
    }

    public void put(String key, String value){
        if(map.containsKey(key)) {
            Node node = map.get(key);
            node.setValue(value);

            deleteFromList(node);
            setListHead(node);
        } else {
            if(map.size()>=capacity) {
                map.remove(tail.getKey());
                deleteFromList(tail);
            }

            Node node = new Node(key, value);
            map.put(key, node);
            setListHead(node)
        }
    }

    private void setListHead(Node node){
        Node tailPrev = tail.prev;

        tail.prev = null;
        tail.next = head;
        head.prev = tail;
        tailPrev.next = null;
    }

    private void deleteFromList(Node node){
        Node nodePrev = node.prev;
        Node NodeNext = node.next;

        node.prev = node.next = null
        nodePrev ? nodePrev.next = NodeNext : null;
        nodeNext ? nodeNext.prev = nodePrev : null; 
    }

}