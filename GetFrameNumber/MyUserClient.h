#ifndef MyUserClient_h
#define MyUserClient_h

#include <IOKit/IOUserClient.h>
#include "MyKext.h"

class MyUserClient : public IOUserClient
{
    OSDeclareDefaultStructors(MyUserClient)
    
private:
    MyKext *fProvider;
    task_t fTask;
    
public:
    virtual bool initWithTask(task_t owningTask, void *securityID, UInt32 type, OSDictionary *properties) override;
    virtual void free() override;
    virtual IOReturn clientClose() override;
    virtual IOReturn clientDied() override;
    virtual bool start(IOService *provider) override;
    virtual void stop(IOService *provider) override;
    
    virtual IOReturn externalMethod(uint32_t selector, IOExternalMethodArguments *arguments,
                                    IOExternalMethodDispatch *dispatch, OSObject *target, void *reference) override;
    
    static IOReturn sGetPhysicalAddress(OSObject *target, void *reference, IOExternalMethodArguments *arguments);
    static IOReturn sGetPMCCNTR(OSObject *target, void *reference, IOExternalMethodArguments *arguments);

};

#endif /* MyUserClient_h */