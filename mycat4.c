#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

size_t get_page_size() {
    static size_t page_size = 0;
    if (page_size == 0) {
        page_size = sysconf(_SC_PAGESIZE);
        if (page_size == (size_t)-1) {
            page_size = 4096; // 默认值
        }
    }
    return page_size;
}

void* align_alloc(size_t size) {
    size_t page_size = get_page_size();
    size_t allocate_size = size + page_size - 1;
    void* ptr = malloc(allocate_size + sizeof(void*));
    
    if (!ptr) return NULL;
    
    void* aligned_ptr = (void*)(((size_t)ptr + sizeof(void*) + page_size - 1) & ~(page_size - 1));
    
    *((void**)((char*)aligned_ptr - sizeof(void*))) = ptr;
    
    return aligned_ptr;
}

void align_free(void* aligned_ptr) {
    if (!aligned_ptr) return;
    void* original_ptr = *((void**)((char*)aligned_ptr - sizeof(void*)));
    free(original_ptr);
}

size_t io_blocksize(const char* filename) {
    struct stat file_stat;
    size_t buffer_size = get_page_size();
    
    if (stat(filename, &file_stat) == 0) {
        size_t fs_block_size = file_stat.st_blksize;
        
        if (fs_block_size > 0 && (fs_block_size & (fs_block_size - 1)) == 0) {
            buffer_size = get_page_size();
            while (buffer_size % fs_block_size != 0) {
                buffer_size += get_page_size();
            }
        }
    }
    
    if (buffer_size > 1024 * 1024) {
        buffer_size = 1024 * 1024;
    }
    
    return buffer_size;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    size_t buffer_size = io_blocksize(argv[1]);
    
    char* buffer = align_alloc(buffer_size);
    if (!buffer) {
        perror("align_alloc");
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd == -1) {
        perror("open");
        align_free(buffer);
        return EXIT_FAILURE;
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
                return EXIT_FAILURE;
            }
            bytes_written += n;
        }
    }

    if (bytes_read == -1) {
        perror("read");
    }

    align_free(buffer);
    close(fd);
    return EXIT_SUCCESS;
}