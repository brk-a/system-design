# sys arch and design for tinder
### features
1. storing profiles
    - PII
    - images (say, five per user)
2. recommending matches
    - MAUs
    - 
3. noting matches
    - probability of a match (per user)
    - 
4. DMs
### storing images
* file or blob?
    - blob &rarr; binary large object
* db has the following features: mutability, transaction guarantees, indexes and access control; plan accordingly
    - mutability: will you change the image? you could, but why do that when you can, simply, create a new row in the db? this is a feature we do not need
    - transaction guarantee: there is no need to enforce atomicity of a transaction w.r.t. images. this is a feature we do not need
    - indexes: are great for searche, sorting etc; this is a feature we do not need
    - access control: files are cheaper and faster than blobs. also, files are static, therefore, one can build a CDN over them
* db will store all the data, of course, however, it requires reference to the image file

    