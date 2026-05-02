#include "MyUserClient.h"

#define super IOUserClient
OSDefineMetaClassAndStructors(MyUserClient, IOUserClient)

bool MyUserClient::initWithTask(task_t owningTask, void *securityID, UInt32 type, OSDictionary *properties)
{
    if (!super::initWithTask(owningTask, securityID, type, properties))
        return false;
    
    fTask = owningTask;
    return true;
}

void MyUserClient::free()
{
    super::free();
}

IOReturn MyUserClient::clientClose()
{
    if (!isInactive())
        terminate();
    
    return kIOReturnSuccess;
}

IOReturn MyUserClient::clientDied()
{
    return clientClose();
}

bool MyUserClient::start(IOService *provider)
{
    if (!super::start(provider))
        return false;
    
    fProvider = OSDynamicCast(MyKext, provider);
    if (!fProvider)
        return false;
    
    return true;
}

void MyUserClient::stop(IOService *provider)
{
    super::stop(provider);
}

IOReturn MyUserClient::externalMethod(uint32_t selector, IOExternalMethodArguments *arguments,
                                      IOExternalMethodDispatch *dispatch, OSObject *target, void *reference)
{
    switch (selector) {
        case 0:
            return sGetPhysicalAddress(this, reference, arguments);
        default:
            return kIOReturnUnsupported;
    }
}

IOReturn MyUserClient::sGetPhysicalAddress(OSObject *target, void *reference, IOExternalMethodArguments *arguments)
{
    MyUserClient *me = OSDynamicCast(MyUserClient, target);
    if (!me || !arguments || arguments->scalarInputCount != 1)
        return kIOReturnBadArgument;
    
    uint64_t virtualAddress = arguments->scalarInput[0];
    uint64_t physicalAddress = 0;
    
    IOReturn result = MyKext::getPhysicalAddress(virtualAddress, &physicalAddress);
    
    arguments->scalarOutput[0] = physicalAddress;
    arguments->scalarOutputCount = 1;
    
    return result;
}
