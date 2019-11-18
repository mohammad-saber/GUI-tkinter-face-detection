
# Mohammad Saber ; Nov 20th 2019

# GUI for playing a video file (containing human face) and detecting face.

# After detection, it saves the detected face as a video file.

# Input data is a "mp4" or "avi" video file.


from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from shutil import copyfile
import time, os
import cv2


class videoGUI:

    def __init__(self, window, window_title):

        self.window = window
        self.window.title(window_title)

        self.pause = False   # Parameter that controls pause button
        self.record_face_status = False   # Parameter that controls face detection and cropping face

        # After it is called once, the show_frame method will be automatically called every delay (milliseconds)
        self.delay = 40   # ms [1000 ms / 25 frames = 40 ms / frame]

        self.cascPath = "haarcascade_frontalface_default.xml"   # OpenCV face detector
        self.faceCascade = cv2.CascadeClassifier(self.cascPath)

        self.result_video = 'output.mp4'   # filename to save output video file
        self.result_frame_size = (200, 200)  # Final frame size to save video file

        # Define the codec and create VideoWriter object, 'avi' works fine with DIVX codec
        self.fourcc = cv2.VideoWriter_fourcc(*'DIVX')

        ##### GUI Design #####
        top_frame = Frame(self.window)
        top_frame.pack(side=TOP, pady=5)

        bottom_frame = Frame(self.window)
        bottom_frame.pack(side=BOTTOM, pady=5)

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(top_frame)
        self.canvas.pack()

        # Select Button
        self.btn_select=Button(bottom_frame, text="Select video file", width=15, command=self.open_file)
        self.btn_select.grid(row=0, column=0)

        # Play Button
        self.btn_play=Button(bottom_frame, text="Play", width=15, state=DISABLED, command=self.play_video)
        self.btn_play.grid(row=0, column=1)

        # Pause Button
        self.btn_pause=Button(bottom_frame, text="Pause", width=15, state=DISABLED, command=self.pause_video)
        self.btn_pause.grid(row=0, column=2)

        # Face Detection Label
        self.lbl_face_detection = Label(bottom_frame, text="Face Detection :", width=15, bg='pink')
        self.lbl_face_detection.grid(row=1, column=0)

        # Face Detection Record
        self.btn_record = Button(bottom_frame, text="Record", width=15, state=DISABLED, command=self.start_record)
        self.btn_record.grid(row=1, column=1)

        # Face Detection Stop Recording
        self.btn_stop = Button(bottom_frame, text="Stop recording", width=15, state=DISABLED, command=self.stop_record)
        self.btn_stop.grid(row=1, column=2)

        # Snapshot Button
        self.btn_snapshot=Button(bottom_frame, text="Snapshot", width=15, state=DISABLED, command=self.snapshot)
        self.btn_snapshot.grid(row=2, column=1)

        # Status bar
        self.status = Label(bottom_frame, text='I am ready !', bd=1, relief=SUNKEN, anchor=W)  # anchor is for text inside Label
        self.status.grid(row=3, columnspan= 3, sticky=E+W)  # side is for Label location in Window

        self.window.mainloop()


    def open_file(self):

        self.pause = False

        self.filename = filedialog.askopenfilename(title="Select file", filetypes=(("MP4 files", "*.mp4"),
                                                                                   ("AVI files", "*.avi")))
        print("\n Filename : ", self.filename, "\n")

        # Open the video file
        self.cap = cv2.VideoCapture(self.filename)

        # Get video source width and height
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.canvas.config(width = self.width, height = self.height)

        self.btn_play['state'] = NORMAL


    def get_frame(self):   # get only one frame

        try:

            if self.cap.isOpened():
                ret, frame = self.cap.read()

                if ret:
                    # Return a boolean success flag and the current frame (color map is BGR)
                    return (ret, frame)
                else:
                    return (ret, None)

            else:
                raise ValueError("Unable to open video file : ", self.filename)

        except:
            messagebox.showerror(title='Video file not found', message='Please select a video file.')


    def play_video(self):

        self.btn_pause['state'] = NORMAL
        self.btn_snapshot['state'] = NORMAL
        self.btn_record['state'] = NORMAL
        self.btn_stop['state'] = NORMAL

        # Get a frame from the video source, and go to the next frame automatically
        ret, frame = self.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))   # convert BGR into RGB color map
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

            if self.record_face_status:
                self.record_face(frame)

        after_id = self.window.after(self.delay, self.play_video)

        if self.pause:
            self.window.after_cancel(after_id)
            self.pause = False


    def pause_video(self):
        self.pause = True
        # self.status['text'] = 'Video paused'
        # print('I am in pause function : ', self.pause)


    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.get_frame()
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".png", frame)


    def record_face(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        # Crop face
        for (x, y, w, h) in faces:
            face_frame = frame[max(0, int(y - 0.1 * h)): min(int(y + h + 0.1 * h), self.height),
                         x:x + w]
            face_frame = cv2.resize(face_frame, self.result_frame_size)

            # write the face_frame
            self.out.write(face_frame)


    def start_record(self):
        self.record_face_status = True
        self.out = cv2.VideoWriter(self.result_video, self.fourcc, fps=25.0, frameSize=self.result_frame_size)
        self.status['text'] = 'Face is being detected'
        start_record_time_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)   # ms
        self.start_record_time = time.strftime('%H:%M:%S', time.gmtime(start_record_time_ms//1000))
        print('Recording face started : ', start_record_time_ms, 'millisecond')
        print('Recording face started : ', self.start_record_time)


    def stop_record(self):
        self.record_face_status = False
        self.status['text'] = 'Face detection was stopped'
        end_record_time_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        self.end_record_time = time.strftime('%H:%M:%S', time.gmtime(end_record_time_ms//1000))
        print('Recording face stopped : ', end_record_time_ms, 'millisecond')
        print('Recording face stopped : ', self.end_record_time)

        self.out.release()   # Release save video file

        new_filename = self.start_record_time + ' - ' + self.end_record_time + os.path.splitext(self.result_video)[-1]
        copyfile(self.result_video, new_filename.replace(':', ' '))


    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

##### End Class #####


# Create a window and pass it to GUI Class
videoGUI(Tk(), "")


