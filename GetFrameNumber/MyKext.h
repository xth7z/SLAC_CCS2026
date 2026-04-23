#ifndef MyKext_h
#define MyKext_h

#include <IOKit/IOService.h>

class MyKext : public IOService
{
    OSDeclareDefaultStructors(MyKext)
    
public:
    virtual bool init(OSDictionary *dictionary = nullptr) override;
    virtual void free() override;
    virtual IOService *probe(IOService *provider, SInt32 *score) override;
    virtual bool start(IOService *provider) override;
    virtual void stop(IOService *provider) override;
    
    static void enableUserModePMU();
    static void disableUserModePMU();
    static IOReturn getPhysicalAddress(uint64_t virtualAddress, uint64_t *physicalAddress);
    static IOReturn getPMCCNTR(uint64_t *value);
};

#endif /* MyKext_h */
