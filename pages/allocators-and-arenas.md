# Better memory management in C

If you are familiar with modern C programming "standards" you may have come across the terms _arena_ and _allocator_. They are both objects used for stricter control over how memory is allocated, used, and freed in a program. Some newer languages implement these in the standard library, [like zig](https://zig.guide/standard-library/allocators/). This article contains an explanation for both, and examples of implementations.

## See you later allocator

The C standard library already contains an implementation for a basic slap heap allocator: `malloc`. The utilities provided were cutting edge at the time of creation and provided dynamic memory allocation of arbitrary sizes, with minimal fragmentation.

However, certain constraints and pitfalls come with having a universally available allocator. One example could be hidden and obfuscated allocations:

```c
// Does this function allocate and return heap memory?
// Or does it return a pointer to a global buffer?
// Does the memory at s have any specific permissions?
char *s = get_user_input();
```

To give the user more control and a better overview of how memory is managed, allocators are used:

```c
Allocator a = get_heap_allocator();

// We now know that the function allocates memory
// and that the memory allocated has permissions
// defined in the heap allocator implementation.
char *s = get_user_input(a);
```

The allocator struct looks like some magic object here, but is actually very simple:

```c
typedef struct Allocator
{
    AllocatorProc proc; // Pointer to a function that does the allocation
    void *data;         // Data used by the allocator for context
} Allocator;

void *heap_allocator_proc(Allocator a, AllocatorMessage msg, u64 size, ...)
{
    switch (msg)
    {
        case MSG_ALLOC:
            // ...
        case MSG_FREE:
            // ...
        case MSG_REALLOC:
            // ...
    }
}

HeapAllocatorData heap_data;

Allocator get_heap_allocator()
{
    return (Allocator){
        .data = (void*)heap_data,
        .proc = heap_allocator_proc,
    };
}

```

```c
// An implementation of strdup without the hidden allocations
void *string_dup(Allocator a, char *original)
{
    char *dup = alloc(a, strlen(original));
    return strcpy(dup, original);
}
```

Now you can have multiple allocators that allocate memory in different ways and use them interchangeably! You will also see explicitly which functions allocate memory, and you can even choose how they do so.

## Entering the arena

For a detailed explanation of arenas check out [this article by Ryan Fleury](https://www.rfleury.com/p/untangling-lifetimes-the-arena-allocator). The following explanation is slightly different, but the idea is the same.

The problem: remembering to free after every allocation can be tricky, and even more so if multiple allocations are made behind the scenes by some utility functions. The solution: memory arenas. When combined with the previously defined `Allocator`, arenas offer straightforward cleanup and scope management.

Arenas are essentially temporary buckets you can fill with data, and then free all at once, making all allocations in the current scope tied to a single source.

```c
Arena a = new_arena(1024);

char *name = arena_alloc(a, 32);
float *temperatures = arena_alloc(a, 10);

// Remember how the string_dup function earlier took an allocator as a parameter?
// Well, now we can make it use the arena to allocate the duplicate string,
// which means it will also be freed along with everything else.
char *name_duplicate = string_dup(get_arena_allocator(a), name);

arena_free(a);
```
