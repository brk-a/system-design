# computer architecture

<div style="text-align: justify;">

## 0. bits and bytes
* computers, at their core, understand zeroes and ones
    * aka bits (binary digits)
* one **bit** is the smallest unit of data in computing
    * denoted as `b`
    * can be zero or one
    * represents absence or presence, off or on, false or true etc
* one **byte** is made up of eight bits
    * denoted as `B`
    * represents characters (strings) or numbers (int, float, double etc)

## 1. disk storage
* is the primary storage of data in a computer
* can be HDD or SDD (as at Mon, 19-Jan-2026 0813h EAT)
* is non-volatile
    * maintains data w/o power (data is persisted when you turn off then turn on your computer)
* contains OS, apps and all user files
* consumer offerings as at time stated above are: 256 GB, 512 GB, 1 TB, 2 TB
* SSDs offer faster data retrieval compared to HDDs; partially explains why they are more expensive than the latter
    * SSD read speed is typically 500 MB/s - 3.5 GB/s; HDD read speed is typically 80 - 160 MB/s

## 2. RAM
* is the primary active data holder
    * holds data structures, variables and application data that are currently in use or being processed
    * a running app's variables, runtime stack etc are stored here
* has quick read/access and write time
    * read/write speed istypically over 5 GB/s
* is volatile
    * does not maintain data when computer loses power (data is not persisted when you turn off then turn on your computer)
* consumer offerings: 4 GB, 8 GB, 16 GB, 32 GB and 64 GB

## 3. cache
* smaller than RAM, however, the read/write times are typically in nanoseconds
    * L1 cache, for example, has a read/write time of B/s
* CPU checks L1 cache, L2 then L3 caches and RAM for data in that order
* a cache's purpose is to reduce the time it takes to access data; frequently used data is stored here
    * consequence: CPU performance is optimised

## 4. CPU
* the *"brain"* of the computer
* fetches, decodes and executes instructions
    * your code is run by the CPU
* understands zeroes and ones, therefore, a compiler turns your ~~crappy~~ code into machine code (zeroes and ones) which are then executed by the CPU
* reads/writes from/to disk, RAM or cache

## 5. motherboard
* aka main board
* the component that holds everything
    * ~~the *"glue that holds everything together"* ahh sh!t~~
* provides the means that allows data and power (electricity) to flow between all the components mentioned above

</div>