# Importing important library
import uvicorn
import cv2
import asyncio
from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer
from starlette.routing import Route
from starlette.responses import StreamingResponse

# Initializing WebGear app with the valid source and enable logging for debugging
web = WebGear(source='../static/video/my_video.mp4',logging=False)

# Creating our own frame producer
async def frame_rate():
    while True:
        frame = web.stream.read()
        if frame is None:
            break
        # For more performance reducing frames.
        frame = reducer (frame,percentage=20)
        # Handeling JPEG endoding
        encodedimage = cv2.imencode('.jpg',frame)[1].tobytes()
        # Yielding frames in byte.
        yield (b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+encodedimage+b'\r\n')
        await asyncio.sleep(0.01)

# Creating our own streaming response server.
async def video_server(scope):
    assert scope['type']== 'http'
    return StreamingResponse('frame_producer()',media_type='multipart/x-mixed-replace; boundary=frame')

# Appending new route to our streaming response server.
web.routes.append(Route('/my_frame',endpoint=video_server))

# Running this app on the uvicorn server.
if __name__ == "__main__":
    uvicorn.run(web(),host='localhost',port=8000)

# Closing app safely.
web.shutdown()