#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/mman.h>

size_t io_blocksize() {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size == -1) {
        return 4096;
    }
    return (size_t)page_size;
}

void* align_alloc(size_t size) {
    size_t page_size = io_blocksize();
    size_t allocate_size = size + page_size - 1;
    void* ptr = malloc(allocate_size);

    if (!ptr) return NULL;

    void* aligned_ptr = (void*)(((size_t)ptr + page_size - 1) & ~(page_size - 1));

    *((void**)((char*)aligned_ptr - sizeof(void*))) = ptr;

    return aligned_ptr;
}

void align_free(void* ptr) {
    if (!ptr) return;
    void* original_ptr = *((void**)((char*)ptr - sizeof(void*)));
    free(original_ptr);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd == -1){
        perror("open");
        exit(EXIT_FAILURE);
    }

    size_t buffer_size = io_blocksize();
    char *buffer = align_alloc(buffer_size);
    if (!buffer) {
        perror("align_alloc");
        close(fd);
        exit(EXIT_FAILURE);
    }

    ssize_t bytes_read;

    while ((bytes_read = read(fd, buffer, buffer_size)) > 0) {
        ssize_t bytes_written = 0;
        while (bytes_written < bytes_read) {
            ssize_t n = write(STDOUT_FILENO, buffer + bytes_written, bytes_read - bytes_written);
            if (n == -1) {
                perror("write");
                align_free(buffer);
                close(fd);
                exit(EXIT_FAILURE);
            }
            bytes_written += n;
        }
    }

    if (bytes_read == -1) {
        perror("read");
        align_free(buffer);
        close(fd);
        exit(EXIT_FAILURE);
    }

    align_free(buffer);
    close(fd);
    return EXIT_SUCCESS;
}