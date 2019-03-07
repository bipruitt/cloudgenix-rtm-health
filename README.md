
CloudGenix Real Time Media Health Report
------------

#### Synopsis
This utility will pull all of the RTM flows (specific app required) for a site over a period of time and write the details of any flow that violate a packet loss threshold to a csv file.

#### Requirements
* Active CloudGenix Account
* Python >= 2.7
* Python modules:
    * cloudgenix >=5.1.1b1 - <https://github.com/CloudGenix/sdk-python>
    * cloudgenix-idname >=1.1.2 - <https://github.com/ebob9/cloudgenix-idname>
* A compute system with the following:
  * Virtual or Physical hardware.
    * x86, amd_64, or ARM architecture.
    * x86/amd_64: 2 vCPU/cores, 2 GB memory, 8 GB storage.
  * ARM: 2 vCPU/cores, 2 GB memory, 8 GB storage.
  * Python 2.7-capable operating system installed.
    * Tested with Ubuntu 16.04 (x86/amd_64/ARM) and Windows (amd_64).
    * Recommended ‘pip’ python package manager.

#### Installation Steps

1. Download the CloudGenix Real Time Media Health Report
2. Extract the code bundle to a directory.
3. In the extracted directory, use pip to ensure required packages are installed.

#### License
MIT

#### Version
Version | Changes
------- | --------
**1.0.0**| Initial Release.

