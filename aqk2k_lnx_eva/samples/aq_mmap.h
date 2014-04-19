/*
	CAqMmap	- Memory Mapped file (for Linux)

	2013/06/16	N.Yamazaki(AQUEST) Creation
*/
// 
#ifndef AQ_MMAP_H
#define AQ_MMAP_H

#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

template <class T> class CAqMmap {
private:
	size_t	size;
	T		*data;

public:
	CAqMmap(): data(0) {}
	virtual ~CAqMmap() { this->close(); }

	T&		 operator[](size_t n) { return *(data + n); }
	const T& operator[](size_t n) const { return *(data + n); }
	T*		 begin()		   { return data; }
	const T* begin()	const  { return data; }
	T*		 end()			   { return data + size; }
	const T* end()		const  { return data + size; }

	size_t GetSize()	{ return size; }
	size_t GetCount()	{ return size/sizeof(T); }
	bool   IsEmpty()	{ return(size == 0); }

	bool open(const char *filename) {
		close();

		int    fd;
		if((fd = ::open(filename, O_RDONLY)) < 0){
			return false;
		}

		struct stat st;
		if(fstat(fd, &st) < 0){
			::close(fd);
			return false;
		}

		size = st.st_size;

		void *p;
		if((p = mmap(0, size, PROT_READ, MAP_SHARED, fd, 0))== MAP_FAILED){
			::close(fd);
			return false;
		}
		data = reinterpret_cast<T *>(p);

		::close(fd);	// not unmap
	    return true;
	}

	void close() {
	    if (data) {
	      munmap(reinterpret_cast<char *>(data), size);
	      data = 0;
	    }
	}

};
#endif
