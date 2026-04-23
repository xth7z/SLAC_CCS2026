KEXT_NAME = MyKext
BUNDLE_ID = com.yourcompany.MyKext

ARCH = arm64e

SDK_PATH = $(shell xcrun --sdk macosx --show-sdk-path)

CC = xcrun -sdk macosx clang
CXX = xcrun -sdk macosx clang++

CFLAGS = -arch $(ARCH) \
         -fno-exceptions \
         -fno-rtti \
         -mkernel \
         -nostdinc \
         -std=c++17 \
         -Wno-inconsistent-missing-override \
         -isysroot $(SDK_PATH) \
         -iframework $(SDK_PATH)/System/Library/Frameworks \
         -I$(SDK_PATH)/System/Library/Frameworks/Kernel.framework/Headers \
         -I$(SDK_PATH)/System/Library/Frameworks/Kernel.framework/Headers/mach \
         -I$(SDK_PATH)/System/Library/Frameworks/Kernel.framework/Headers/bsd \
         -I$(SDK_PATH)/System/Library/Frameworks/Kernel.framework/PrivateHeaders \
         -target arm64e-apple-macos \
         -DKERNEL -DKERNEL_PRIVATE -DDRIVER_PRIVATE -DAPPLE -DNeXT

CXXFLAGS = $(CFLAGS) \
           -nostdinc++ \
           -I$(SDK_PATH)/System/Library/Frameworks/Kernel.framework/Headers/c++

LDFLAGS = -arch $(ARCH) \
          -Xlinker -kext \
          -nostdlib \
          -lkmod \
          -lcc_kext \
          -target arm64e-apple-macos

SRCS = MyKext.cpp MyUserClient.cpp
OBJS = $(SRCS:.cpp=.o)

BUILD_DIR = build
KEXT_DIR = $(BUILD_DIR)/$(KEXT_NAME).kext
KEXT_CONTENTS = $(KEXT_DIR)/Contents
KEXT_MACOS = $(KEXT_CONTENTS)/MacOS

all: $(KEXT_DIR)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(KEXT_DIR): $(OBJS)
	mkdir -p $(KEXT_MACOS)
	$(CXX) $(LDFLAGS) -o $(KEXT_MACOS)/$(KEXT_NAME) $(OBJS)
	cp Info.plist $(KEXT_CONTENTS)/
	touch $(KEXT_DIR)

clean:
	rm -rf $(BUILD_DIR) *.o

install: $(KEXT_DIR)
	sudo cp -R $(KEXT_DIR) /Library/Extensions/
	sudo kextload /Library/Extensions/$(KEXT_NAME).kext

uninstall:
	sudo kextunload /Library/Extensions/$(KEXT_NAME).kext
	sudo rm -rf /Library/Extensions/$(KEXT_NAME).kext

.PHONY: all clean install uninstall