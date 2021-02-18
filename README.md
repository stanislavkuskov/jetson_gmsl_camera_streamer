# jetson_gmsl_camera_streamer

Camera streamer with gmsl board and cameras based on opencv (gstreamer backend)

**HARDWARE:** Jetson AGX Xavier Dev kit, Conecttech GMSL2 camera board JCB004, Leopard Imaging IMX390 GMSL2 cameras

**SOFTWARE:** JetPack 4.4 with Conecttech GMSL2 camera board driver for Leopard Imaging IMX390 GMSL2 cameras, fixed argus library, fixed nvarguscamerasrc gstreamer plugin.

## Getting started

- Connect JCB004, cameras, power supply for JBC004 and Xavier 
- Install JetPack 4.4 on Xavier by manual (from CTI drivers package)

## Fixes

Some important fixes for stabilization of camera working.

- **[argus_camera](https://forums.developer.nvidia.com/t/141432/9)** - fix user compile argus_camera application from the release sources causes segmentation fault (SIGSEGV)

- **[nvarguscamerasrc](https://forums.developer.nvidia.com/t/issue-with-multi-camera-capture-using-released-nvarguscamerasrc-code-for-jetpack-4-4/147837/15?u=shaneccc)** - public release source code built the libgstnvarguscamera.so can not launch multiple cameras.


- **[nvarguscamerasrc](https://forums.developer.nvidia.com/t/160811/6)** - patch for fixing memory leak

- undocumented bug - **[bluedroid_pm]**

    Bluetooth Bluedroid power management Driver. Irq of this module can overload cpu usage and Jetson reboots offten (especially with hight temperature).

    ```bash
    sudo nano /etc/modprobe.d/blacklist.conf
    ```
    Add string - ```install bluedroid_pm /bin/false``` 

## Run cameras

clone this repository and run

```bash
python3 streamer_example.py
```
## Important features

- **Disable gstreamer buffer (30 frames) for elimination of delay**
    
    It helps when you want read frames with lower speed than cameras speed(30 fps). Just add:
    ```python
    max-buffers=1 drop=True
    ```
    to gstreamer source string for OpenCV.

- **Use daemon threads** 
    
    Run camera read method in deamon thread and close each if can not read frame. It helps to avoid error
    ```
    Jan 27 11:52:55 jetson nvargus-daemon[6225]: (Argus) Error InvalidState:  (propagating from src/api/ScfCaptureThread.cpp, function run(), line 109)
    Jan 27 11:52:55 jetson nvargus-daemon[6225]: SCF: Error InvalidState: Session has suffered a critical failure (in src/api/Session.cpp, function capture(), line 667)
    ```
    and fast increasing syslog file size (this error write in syslog infinitely).
- **Get camera parameters**

    Get and change parameters of gstreamer source string.
    Get:
    ```bash
    gst-inspect-1.0 nvarguscamerasrc
    ```
    Change (add parameter into gstreamer source string after nvarguscamerasrc, for example "tnr-strength"): 

    ```python
    nvarguscamerasrc tnr-strength=0
    ```
## In bugfixing process:
- [Some of cameras freeze](https://forums.developer.nvidia.com/t/multiple-camera-streams-freeze-imx390/168664)

    When started “multi session” in argus_camera example some of cameras freeze randomly (stream_example.py work well)
