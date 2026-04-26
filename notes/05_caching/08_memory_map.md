## Memory Map

`mmap`, short for **memory map**, is an operating system mechanism that maps a file or device directly into a process’s virtual memory address space. Instead of reading file data explicitly with `read()` into a buffer, the application can access the file as if it were an array in memory. The operating system loads pages from disk into RAM on demand.

`mmap` is commonly used in databases, search engines, embedded storage engines, file parsers, shared-memory communication, and high-performance systems that need efficient access to large files.

The key idea is that the application works with memory addresses, while the operating system handles paging data in and out.

```text id="u4eap0"
+---------------------+
| Application Process |
+----------+----------+
           |
           | reads memory address
           v
+---------------------+
| Virtual Memory      |
| mmap region         |
+----------+----------+
           |
           | page fault if page not loaded
           v
+---------------------+
| OS Page Cache       |
+----------+----------+
           |
           | disk I/O if page not cached
           v
+---------------------+
| File on Disk        |
+---------------------+
```

Example use case:

```json id="qsftup"
{
  "file": "users.dat",
  "size": "4GB",
  "accessPattern": "random reads",
  "approach": "map file into memory and access needed offsets"
}
```

With `mmap`, the process does not need to manually load the whole file. Pages are brought into memory as they are touched.

### Concepts

`mmap` sits at the boundary between file I/O and virtual memory. To understand it, it helps to understand virtual memory, pages, page faults, and the operating system page cache.

#### Memory-Mapped Files

A memory-mapped file is a file whose contents are exposed as a range of virtual memory addresses.

Instead of doing this:

```c id="g8uz1i"
read(fd, buffer, size);
```

The application can do something like this:

```c id="nk5o36"
char *data = mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, 0);
char first_byte = data[0];
```

The application accesses `data[0]` like normal memory. If that part of the file is not already in RAM, the operating system loads the corresponding page from disk.

Example:

```json id="7tdhjf"
{
  "fileOffset": 0,
  "virtualAddress": "0x7f00...",
  "access": "data[0]",
  "osAction": "load page if needed"
}
```

The application does not directly manage the read buffer. The OS maps file pages into the process address space.

#### Virtual Memory and Pages

Operating systems manage memory in fixed-size chunks called **pages**. A common page size is 4 KiB, though larger pages also exist.

When a file is memory-mapped, the mapping is page-based. Accessing a byte causes the OS to load the whole page containing that byte.

Example:

```text id="rl6gsm"
File:
Offset 0       4096       8192       12288
   | Page 0 | Page 1 | Page 2 | Page 3 |

Access byte at offset 5000.
OS loads Page 1.
```

Example output:

```json id="gy3d9y"
{
  "accessedOffset": 5000,
  "pageSize": 4096,
  "loadedPage": 1
}
```

This matters because random access may cause many page faults, while sequential access allows the OS to read ahead efficiently.

#### Page Faults

A page fault happens when the process accesses a mapped memory page that is not currently loaded into RAM.

For `mmap`, a page fault does not necessarily mean an error. It often means the OS must load the requested file page from disk into memory.

Example flow:

```text id="i6tj7g"
1. Application accesses mapped address.
2. Page is not in RAM.
3. CPU triggers page fault.
4. Kernel loads file page from disk or page cache.
5. Application continues as if it read memory.
```

Example page fault result:

```json id="39y8ow"
{
  "event": "page_fault",
  "pageLoadedFrom": "disk",
  "applicationVisibleError": false
}
```

Page faults are normal, but too many major page faults can hurt performance because they require disk I/O.

#### OS Page Cache

The OS page cache stores file data in RAM. Both `read()` and `mmap()` usually use the page cache.

With `read()`, the kernel copies data from the page cache into an application buffer. With `mmap()`, the application can access the page cache-backed memory more directly.

Simplified comparison:

```text id="c588z9"
read():
Disk -> OS page cache -> copy into user buffer -> application

mmap():
Disk -> OS page cache -> mapped into process address space -> application
```

Example:

```json id="1npa0b"
{
  "read": "requires explicit syscall and copy into buffer",
  "mmap": "uses page faults and mapped pages"
}
```

This can make `mmap` attractive for workloads that repeatedly access parts of large files.

### Basic mmap Example

A simple example is mapping a file and reading bytes from it.

Example C code:

```c id="t24lsg"
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

int main() {
    int fd = open("example.txt", O_RDONLY);

    struct stat st;
    fstat(fd, &st);

    char *data = mmap(
        NULL,
        st.st_size,
        PROT_READ,
        MAP_PRIVATE,
        fd,
        0
    );

    if (data == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("First byte: %c\n", data[0]);

    munmap(data, st.st_size);
    close(fd);

    return 0;
}
```

Example file:

```text id="1cuvj6"
Hello mmap!
```

Example output:

```text id="5hgv09"
First byte: H
```

The file is accessed through memory. The OS loads file pages as needed.

### mmap Flags and Modes

`mmap` behavior depends on protection flags and mapping flags. These define whether the memory can be read, written, shared, or private.

#### Protection Flags

Protection flags describe what the process is allowed to do with the mapped memory.

Common flags:

| Flag         | Meaning                  |
| ------------ | ------------------------ |
| `PROT_READ`  | Pages can be read        |
| `PROT_WRITE` | Pages can be written     |
| `PROT_EXEC`  | Pages can be executed    |
| `PROT_NONE`  | Pages cannot be accessed |

Example read-only mapping:

```c id="um5kki"
mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, 0);
```

Example read-write mapping:

```c id="9z3fbo"
mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
```

Example result:

```json id="85wsfp"
{
  "protection": ["read", "write"],
  "writesAllowed": true
}
```

Do not map data as executable unless you truly need executable memory. Executable mappings can increase security risk.

#### MAP_PRIVATE

`MAP_PRIVATE` creates a private copy-on-write mapping. Changes made by the process are not written back to the original file.

Example:

```c id="8w1q63"
char *data = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
data[0] = 'X';
```

The process sees the modified byte, but the file is unchanged.

Example:

```json id="ml34l2"
{
  "mapping": "MAP_PRIVATE",
  "processSeesChange": true,
  "fileChanged": false
}
```

`MAP_PRIVATE` is useful when you want to read a file and possibly modify the mapped memory without altering the file.

#### MAP_SHARED

`MAP_SHARED` allows changes to be written back to the mapped file and potentially seen by other processes mapping the same file.

Example:

```c id="mljv0d"
char *data = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
data[0] = 'X';
msync(data, size, MS_SYNC);
```

Example result:

```json id="1ikfd4"
{
  "mapping": "MAP_SHARED",
  "fileChanged": true,
  "otherProcessesCanSeeChange": true
}
```

`MAP_SHARED` is useful for file-backed shared state, memory-mapped databases, and inter-process communication. It also requires more care because writes affect persistent data.

#### Anonymous Mapping

`mmap` can also allocate memory not backed by a file. This is called anonymous mapping.

Example:

```c id="tpko4g"
void *mem = mmap(
    NULL,
    4096,
    PROT_READ | PROT_WRITE,
    MAP_PRIVATE | MAP_ANONYMOUS,
    -1,
    0
);
```

Example result:

```json id="b77beo"
{
  "mapping": "anonymous",
  "backingFile": false,
  "useCase": "allocate memory directly from OS"
}
```

Anonymous mappings are used by memory allocators, runtimes, shared memory systems, and low-level infrastructure.

### mmap vs read()

Both `mmap` and `read()` can be used to access file data, but they have different trade-offs.

| Aspect            | `read()`                                     | `mmap()`                                    |
| ----------------- | -------------------------------------------- | ------------------------------------------- |
| Programming model | Explicit read into buffer                    | Access file as memory                       |
| Syscalls          | Repeated reads may require repeated syscalls | Initial mapping, then page faults           |
| Copying           | Kernel copies data to user buffer            | Can avoid some copying                      |
| Access pattern    | Good for streaming sequential reads          | Good for random access and repeated reads   |
| Error model       | `read()` returns errors directly             | Access may trigger signals such as `SIGBUS` |
| Memory pressure   | Application controls buffers                 | OS controls mapped pages                    |
| Complexity        | Simpler                                      | More subtle edge cases                      |

Example sequential read:

```c id="1xqcrb"
while ((n = read(fd, buffer, sizeof(buffer))) > 0) {
    process(buffer, n);
}
```

This is simple and often excellent for streaming through a file once.

Example random access with `mmap`:

```c id="l9iays"
record = data + record_offset;
process(record);
```

This is convenient when the application frequently jumps to different offsets.

Example decision:

```json id="ly6h0t"
{
  "useReadFor": "simple sequential streaming",
  "useMmapFor": "large files with random or repeated access"
}
```

`mmap` is not always faster. Its performance depends on workload, access pattern, file size, memory pressure, and page fault behavior.

### Common Usage Patterns

`mmap` appears in many systems where file data is large, structured, or accessed repeatedly.

#### Large File Parsing

If a file is large and the application needs random access to parts of it, `mmap` can simplify parsing.

Example:

```json id="hzrtt2"
{
  "file": "index.bin",
  "size": "20GB",
  "accessPattern": "random lookup by offset",
  "mmapBenefit": "avoid manual read/seek buffer management"
}
```

Example access:

```c id="frxcn0"
char *record = mapped_file + offset;
```

This is common in search indexes, binary formats, and read-only data files.

#### Database Storage Engines

Some storage engines use memory-mapped files to access database pages. Instead of managing their own buffer pool entirely, they rely partly on the OS page cache.

Example conceptual database page access:

```text id="mg6z8p"
Database needs page 42.
Page 42 corresponds to file offset 42 * page_size.
Storage engine reads mapped memory at that offset.
OS loads page if needed.
```

Example:

```json id="3mbhix"
{
  "databasePage": 42,
  "pageSize": 4096,
  "fileOffset": 172032
}
```

Some embedded databases and older storage designs rely heavily on `mmap`. Other databases prefer explicit I/O and their own buffer pool to control caching more precisely.

#### Search Indexes

Search engines often store index segments as immutable files. `mmap` is a good fit for read-only or mostly read-only index files because the OS can page in only the portions that are queried.

Example:

```json id="voy002"
{
  "segment": "index_segment_17",
  "mapping": "read-only",
  "accessPattern": "random term lookups"
}
```

When a query touches a term dictionary or posting list, the relevant pages are loaded on demand.

#### Shared Memory Between Processes

Multiple processes can map the same file with `MAP_SHARED` and communicate through it.

Example:

```text id="0bn4fo"
Process A maps shared.dat.
Process B maps shared.dat.
Process A writes value.
Process B reads value.
```

Example shared state:

```json id="s5d28x"
{
  "sharedCounter": 42,
  "visibleToProcesses": ["process-a", "process-b"]
}
```

This can be very fast, but synchronization is required. `mmap` itself does not provide locks or atomic coordination. Processes must use mutexes, futexes, semaphores, file locks, or atomic operations where appropriate.

#### Memory-Mapped Logs

Some systems use memory-mapped files for append-heavy logs or queue-like structures. The application writes to mapped memory, and the OS flushes dirty pages to disk.

Example:

```json id="gqiaov"
{
  "file": "commit.log",
  "mapping": "MAP_SHARED",
  "writePattern": "append records",
  "flush": "msync or OS writeback"
}
```

This can reduce syscall overhead, but durability must be handled carefully. A write to mapped memory is not necessarily durable until flushed.

### Durability and Flushing

With `MAP_SHARED`, writes modify memory-backed file pages. The OS eventually flushes dirty pages to disk, but not necessarily immediately.

To force flushing, applications can use `msync`.

Example:

```c id="yy9ya6"
data[0] = 'X';
msync(data, size, MS_SYNC);
```

Example result:

```json id="19hrxr"
{
  "writeVisibleInMemory": true,
  "msyncCalled": true,
  "writeRequestedToDisk": true
}
```

Important distinction:

```text id="0ch1kx"
Writing to mmap memory changes the mapped page.
It does not automatically mean the data is safely persisted to disk immediately.
```

If the system crashes before dirty pages are flushed, recent changes may be lost.

For stronger durability, applications may need:

```text id="0sna90"
msync()
fsync()
careful write ordering
checksums
journaling
copy-on-write formats
```

This is why database systems must be careful when using `mmap` for writable files.

### mmap and Performance

`mmap` can improve performance in some cases, but it can also cause performance surprises.

#### Benefits

`mmap` can reduce syscall overhead because the application does not need to call `read()` for every small access. It can also avoid copying data from kernel buffers into user-space buffers.

Example benefit:

```json id="jyd802"
{
  "workload": "random reads from large immutable index",
  "benefit": "OS loads only touched pages"
}
```

It can also simplify code for random access:

```c id="dn4i9h"
uint32_t value = *(uint32_t *)(data + offset);
```

The file behaves like a memory array.

#### Costs

`mmap` can be slower if it causes many random page faults. A page fault is more expensive than a simple memory access, especially if it requires disk I/O.

Example problem:

```json id="ilxla3"
{
  "accessPattern": "random access across 500GB file",
  "ram": "32GB",
  "problem": "constant major page faults"
}
```

Memory pressure can also cause mapped pages to be evicted, leading to repeated page faults.

Another cost is less explicit control. With `read()`, the application decides exactly what to load and when. With `mmap`, the OS decides paging behavior.

#### Sequential vs Random Access

For simple sequential scans, `read()` can be just as good or better because it is predictable and easy for the OS to prefetch.

For random access, `mmap` can be more convenient and sometimes faster because the application can jump directly to offsets.

Example decision:

```json id="xsn8fd"
{
  "sequentialLogProcessing": "read() is often simpler",
  "randomIndexLookup": "mmap may be convenient and efficient"
}
```

The best choice should be tested with the real workload.

### mmap Safety Issues

`mmap` introduces some edge cases that are different from normal file reads.

#### SIGBUS When File Is Truncated

If a file is mapped and another process truncates it, the original process may crash with `SIGBUS` when it accesses a part of the mapping that no longer exists.

Example:

```text id="45sqqo"
Process A maps file of size 1GB.
Process B truncates file to 1MB.
Process A accesses offset 500MB.
Process A receives SIGBUS.
```

Example risk:

```json id="3bactb"
{
  "error": "SIGBUS",
  "cause": "mapped region no longer backed by file"
}
```

This is one of the most important `mmap` hazards. Applications should coordinate file truncation carefully or avoid mapping files that may shrink unexpectedly.

#### Bounds Checking

Accessing beyond the mapped size is unsafe and may crash the process.

Example:

```c id="dgzlj3"
char value = data[size + 10]; // invalid access
```

Example result:

```json id="nxzc6y"
{
  "access": "out of bounds",
  "result": "undefined behavior or crash"
}
```

Applications must track file sizes and offsets carefully.

#### Concurrent Writes

If multiple processes write to the same mapped region, the result can be corrupted unless synchronization is used.

Example unsafe behavior:

```text id="4m7ut4"
Process A writes counter = counter + 1.
Process B writes counter = counter + 1.
Both read old value 10.
Both write 11.
Expected 12, actual 11.
```

Example output:

```json id="54o6ke"
{
  "expectedCounter": 12,
  "actualCounter": 11,
  "problem": "lost update"
}
```

`mmap` shares memory, but it does not automatically make updates atomic or safe.

#### File Format Corruption

Writable mappings can corrupt files if the process crashes halfway through an update.

Example:

```json id="h3ua00"
{
  "operation": "update record header and body",
  "crashAfter": "header updated",
  "bodyUpdated": false,
  "fileState": "inconsistent"
}
```

Robust systems use checksums, journaling, copy-on-write pages, versioned records, or append-only designs to recover from partial writes.

### mmap in System Design

In system design, `mmap` often appears when discussing storage engines, search systems, local indexes, high-performance file access, or shared memory.

#### When mmap Is a Good Fit

`mmap` is a good fit when:

```text id="fyqvew"
The file is large.
Access is random or repeated.
The file format is offset-addressable.
The data is mostly read-only.
The OS page cache is acceptable.
The application benefits from simpler pointer-like access.
```

Example:

```json id="lxx1yl"
{
  "system": "search index server",
  "data": "immutable index segments",
  "reason": "random term lookups over large files"
}
```

Immutable or append-only files are especially good candidates because they avoid many concurrency and corruption problems.

#### When mmap Is a Poor Fit

`mmap` may be a poor fit when:

```text id="5hf1i7"
The file changes size frequently.
The file may be truncated by other processes.
The workload is simple sequential streaming.
The application needs strict control over I/O scheduling.
The system must handle memory pressure predictably.
The data requires complex transactional durability.
```

Example:

```json id="o4e3mq"
{
  "system": "high-throughput transactional database",
  "concern": "needs explicit buffer pool and write ordering",
  "mmapFit": "maybe poor"
}
```

Many databases avoid relying fully on `mmap` because they want tighter control over caching, eviction, prefetching, and write durability.

### Concrete Example: Memory-Mapped Lookup Table

Suppose an application has a large read-only binary lookup table. Each record is fixed-width and exactly 128 bytes.

Record location:

```text id="7n7o5r"
offset = record_id * 128
```

Example:

```json id="uryepb"
{
  "recordId": 1000,
  "recordSize": 128,
  "offset": 128000
}
```

With `mmap`, the application can jump directly to that offset:

```c id="i0y8a2"
char *record = data + (record_id * 128);
```

Example result:

```json id="3cl8ov"
{
  "lookup": "record 1000",
  "method": "direct offset into mapped file",
  "databaseQuery": false
}
```

This is useful for local indexes, embedded read-only databases, dictionaries, and precomputed lookup tables.

### Concrete Example: Shared Metrics Region

Two processes can share a memory-mapped file for fast local metrics exchange.

Process A writes:

```c id="7vyjk5"
metrics->request_count += 1;
```

Process B reads:

```c id="mti70b"
printf("%lu\n", metrics->request_count);
```

Conceptual layout:

```text id="b8s497"
+--------------------+
| shared_metrics.dat |
+--------------------+
| request_count      |
| error_count        |
| last_update_time   |
+--------------------+
```

Example output:

```json id="3ngqgi"
{
  "request_count": 154220,
  "error_count": 32
}
```

This can be extremely fast, but only if synchronization is correct. For counters, atomic operations may be needed.

### mmap vs Database Buffer Pool

Some databases rely on the OS page cache through `mmap`, while others implement their own buffer pool using explicit I/O.

#### mmap / OS Page Cache Approach

```text id="jewhtd"
Database reads mapped file.
OS decides which pages stay in RAM.
Page faults load data when touched.
```

Benefits:

```json id="hfcwo0"
{
  "benefit": [
    "simpler storage engine code",
    "OS handles caching",
    "good for read-heavy mapped files"
  ]
}
```

#### Explicit Buffer Pool Approach

```text id="4sxbav"
Database issues read/write calls.
Database manages its own page cache.
Database controls eviction, prefetch, and dirty page flushing.
```

Benefits:

```json id="l0q2ee"
{
  "benefit": [
    "more predictable database behavior",
    "custom eviction policy",
    "tighter control over durability"
  ]
}
```

This trade-off is important in storage engine design. `mmap` gives simplicity and OS integration, while a custom buffer pool gives control.

### Monitoring mmap Behavior

Because `mmap` performance depends on paging, monitor memory and page fault behavior.

Useful things to watch:

```text id="p6zp71"
major page faults
minor page faults
resident set size
page cache usage
I/O wait
disk read latency
memory pressure
swap activity
```

Example monitoring output:

```json id="v0cowg"
{
  "minorPageFaultsPerSecond": 12000,
  "majorPageFaultsPerSecond": 4,
  "rss": "2.4GB",
  "mappedFileSize": "80GB",
  "ioWait": "3%"
}
```

Minor page faults usually mean the page was already in memory but needed to be mapped into the process. Major page faults usually require disk I/O and are more expensive.

High major page faults may indicate that the working set is larger than available memory.

#### Best Practices

1. **Use mmap for large, mostly read-only files with random access** This is one of the best fits.
2. **Avoid mapping files that may be truncated unexpectedly** Truncation can cause `SIGBUS`.
3. **Track file sizes and offsets carefully** Out-of-bounds access can crash the process.
4. **Use `MAP_PRIVATE` for read-mostly data that should not modify the file** It protects the file from accidental writes.
5. **Use `MAP_SHARED` only when writes should affect the underlying file** Combine it with `msync` and careful durability design.
6. **Synchronize concurrent writers** `mmap` does not automatically prevent races.
7. **Test with realistic access patterns** `mmap` performance depends heavily on sequential vs random access and memory pressure.
8. **Monitor major page faults** High major fault rates can cause latency spikes.
9. **Do not assume mmap is always faster than read** Benchmark the real workload.
10. **Design crash-safe file formats for writable mappings** Use checksums, append-only writes, journaling, or copy-on-write techniques.
