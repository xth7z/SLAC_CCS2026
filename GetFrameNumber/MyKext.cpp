#include <IOKit/IOLib.h>
#include <IOKit/IOMemoryDescriptor.h>
#include <mach/mach_types.h>
#include "MyKext.h"
#include "MyUserClient.h"

#define super IOService
OSDefineMetaClassAndStructors(MyKext, IOService)

extern "C" {
    extern kern_return_t _start(kmod_info_t * ki, void *d);
    extern kern_return_t _stop(kmod_info_t *ki, void *d);
}

#define KEXT_VERSION "1.0.0"

__attribute__((visibility("default"))) KMOD_EXPLICIT_DECL(com.yourcompany.MyKext, KEXT_VERSION, _start, _stop)
#ifdef __LP64__
__attribute__((used)) static kern_return_t my_start(kmod_info_t * ki, void *d) {
    return KERN_SUCCESS;
}
__attribute__((used)) static kern_return_t my_stop(kmod_info_t *ki, void *d) {
    return KERN_SUCCESS;
}
__attribute__((used)) static kmod_start_func_t *_realmain = my_start;
__attribute__((used)) static kmod_stop_func_t *_antimain = my_stop;
#endif

bool MyKext::init(OSDictionary *dict)
{
    if (!super::init(dict))
        return false;
    
    IOLog("MyKext::init called\n");
    return true;
}

void MyKext::free(void)
{
    IOLog("MyKext::free called\n");
    super::free();
}

IOService *MyKext::probe(IOService *provider, SInt32 *score)
{
    IOService *result = super::probe(provider, score);
    IOLog("MyKext::probe called\n");
    return result;
}

bool MyKext::start(IOService *provider)
{
    if (!super::start(provider))
        return false;
    
    IOLog("MyKext::start called\n");
    registerService();

    return true;
}

void MyKext::stop(IOService *provider)
{
    IOLog("MyKext::stop called\n");
    super::stop(provider);
}

IOReturn MyKext::getPhysicalAddress(uint64_t virtualAddress, uint64_t *physicalAddress)
{
    if (!physicalAddress) {
        return kIOReturnBadArgument;
    }

    task_t current = current_task();
    if (!current) {
        return kIOReturnError;
    }

    IOMemoryDescriptor *md = IOMemoryDescriptor::withAddressRange(
        virtualAddress, PAGE_SIZE, kIODirectionInOut, current);
    
    if (!md) {
        return kIOReturnNoMemory;
    }

    // lock Memory
    IOReturn prepareResult = md->prepare(kIODirectionInOut);
    if (prepareResult != kIOReturnSuccess) {
        md->release();
        return prepareResult;
    }

    IOPhysicalAddress physAddr = md->getPhysicalAddress();
    *physicalAddress = physAddr;

    // unlock Memory
    md->complete(kIODirectionInOut);

    md->release();

    return kIOReturnSuccess;
}


extern "C" {
    kern_return_t _start(kmod_info_t * ki, void *d)
    {
        return KERN_SUCCESS;
    }

    kern_return_t _stop(kmod_info_t *ki, void *d)
    {
        return KERN_SUCCESS;
    }
}