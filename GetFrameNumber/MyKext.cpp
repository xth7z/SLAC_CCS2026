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

    // enableUserModePMU();
    
    return true;
}

void MyKext::stop(IOService *provider)
{
    // disableUserModePMU();
    IOLog("MyKext::stop called\n");
    super::stop(provider);
}

// void MyKext::enableUserModePMU()
// {
//     asm volatile("msr pmuserenr_el0, %0" : : "r"(0xf));
//     asm volatile("msr pmcntenset_el0, %0" :: "r" ((unsigned long long)(1 << 31)));
//     unsigned long long pmcr_val;
//     asm volatile("mrs %0, pmcr_el0" : "=r" (pmcr_val));
//     pmcr_val |= (1 << 0) | (1 << 6); // Enable all counters and make CCNT 64-bit
//     asm volatile("msr pmcr_el0, %0" : : "r" (pmcr_val));
// }

// void MyKext::disableUserModePMU()
// {
//     unsigned long long pmcr_val;
//     asm volatile("mrs %0, pmcr_el0" : "=r" (pmcr_val));
//     pmcr_val &= ~(1 << 0); // Disable all counters
//     asm volatile("msr pmcr_el0, %0" : : "r" (pmcr_val));
//     asm volatile("msr pmuserenr_el0, %0" : : "r" ((unsigned long long)0));
// }

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


// IOReturn MyKext::getPMCCNTR(uint64_t *pmccntr)
// {
//     if (!pmccntr) {
//         return kIOReturnBadArgument;
//     }

//     uint64_t value;
//     asm volatile("mrs %0, pmccntr_el0" : "=r"(value));
//     *pmccntr = value;

//     return kIOReturnSuccess;
// }

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