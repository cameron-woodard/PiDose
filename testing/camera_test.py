import picamera

input('Press enter to begin previewing camera, then press enter again to stop preview.')     
with picamera.PiCamera() as camera:
    camera.resolution = (256, 256)
    camera.framerate = 30
    camera.vflip = True
    camera.hflip = True
    camera.rotation = 270
    camera.start_preview()
    input()
    camera.stop_preview()

    
