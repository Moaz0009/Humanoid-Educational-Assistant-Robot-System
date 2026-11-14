from STT import whisper_asr
from Face_Detection import detect,upload
from TWD import detect_word
from Qwen_eval import qwen_ar,model_communicator
from Serial_Communication import serial_comm
from Finger_Counter import count_fingers_in_frame
from Emotion_Detection import detect_emotions_in_frame
from tts_arabic import text_to_speech_file, play_audio_file
from Application_Interface.app_connect import *
import time
import sys
correct_path = "audios/correct.mp3"
false_number = "audios/false_number.mp3"
false_ques = "audios/false.mp3"
adult = "audios/get_adult.mp3"
database={}
upload.register_face('Moaz Abdeljalil','moaz.jpg',database)
upload.register_face('Nour Fares','nour.jpg',database)
current_student=''
first=0

import sys
import time
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import threading

class AIGUI(QWidget):
    from PyQt5.QtCore import Qt, QTimer

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Teaching Assistant")
        self.showFullScreen()
        self.data = initialize_and_get_data()

        self.label = QLabel("😴", self)
        self.label.setStyleSheet("font-size: 100px; color: white; background-color: black;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.current_question = 0
        self.identity = None
        self.score = 0
        self.last_finger_number = None
        self.finger_frame_count = 0
        self.true_finger_number = None
        self.required_consistency = 20

        self.database = database
        self.video_timer = QTimer()
        self.cap = None

        QTimer.singleShot(1000, self.start_standby)

    def start_standby(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.label.setText("😴")
        self.label.setStyleSheet("font-size: 100px; color: white; background-color: black;")
        QTimer.singleShot(1000, self.check_trigger_word)

    def check_trigger_word(self):
        if detect_word():
            self.label.setText("Trigger word detected. Verifying identity...")
            self.verify_face()
        else:
            QTimer.singleShot(1000, self.check_trigger_word)

    def verify_face(self):
        self.label.setText("Initializing camera...")
        self.identity = "Unknown"
        self.start_time = time.time()
    
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
    
        self.video_timer.timeout.connect(self.update_camera_feed)
        self.video_timer.start(30)
    
    def update_camera_feed(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            time.sleep(0.5)
    
        ret, frame = self.cap.read()
        if not ret:
            self.label.setText("Camera error.")
            self.video_timer.stop()
            return
    
        # ✅ Detect identity and get the annotated frame
        identity, annotated_frame = detect.detect_verify(frame, self.database)
    
        # ✅ Display the annotated frame
        rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_img).scaled(self.label.width(), self.label.height()))
        QApplication.processEvents()
    
        # ✅ Always wait full 5 seconds before deciding
        elapsed = time.time() - self.start_time
        if elapsed >= 5:
            self.video_timer.stop()
            self.cap.release()
            self.cap = None
    
            if identity != "Unknown":
                self.identity = identity
                self.label.setText(f"Welcome {identity}!\nStarting Q&A...")
                play_audio_file('hello_message.mp3')
                A_Q =  find_child_by_name(self.data,identity)
                self.questions = A_Q['questions']
                self.answers = A_Q['correctAnswers']
                QTimer.singleShot(1500, self.ask_question)
            else:
                self.label.setText("ﻻ يوجد طﻻب هنا.\nالعوده للانتظار.")
                QTimer.singleShot(3000, self.start_standby)
    
    def Finger_Count(self):
        print('In Finger_Count...')
        self.finger_frame_count = 0
        self.last_finger_number = None
        start_time = time.time()
    
        while time.time() - start_time < 7:  # max 5 seconds
            ret, frame = self.cap.read()
            if not ret:
                self.label.setText("Camera error during finger count.")
                return None
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            frame, current_finger_number = count_fingers_in_frame(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_img).scaled(self.label.width(), self.label.height()))
            QApplication.processEvents()
    
            if current_finger_number == self.last_finger_number:
                self.finger_frame_count += 1
            else:
                self.finger_frame_count = 1
                self.last_finger_number = current_finger_number
    
            if self.finger_frame_count >= self.required_consistency:
                print(f"Confirmed finger number: {current_finger_number}")
                return current_finger_number
    
            time.sleep(0.05)  # Avoid CPU overload
    
        print("Finger count timeout")
        return self.last_finger_number  # Return the last seen number instead of None
    def ask_question(self):
        if self.current_question >= len(self.questions):
            self.label.setText(f"لقد انتهت جلستنا!\n{self.identity} الدرجه: {self.score}/{len(self.questions)}")
            play_audio_file('goodbye_message.mp3')
            self.current_question = 0
            self.score = 0
            QTimer.singleShot(5000, self.start_standby)
            return

        question = self.questions[self.current_question]
        self.label.setText(f"Q{self.current_question+1}: {question})")
        QApplication.processEvents()

        audio_path = text_to_speech_file(text=question, output_path="question.mp3", lang='ar')
        play_audio_file('question.mp3')

        if self.current_question in [1, 3, 5]:
            print('number')
            serial_comm.send(question[-1])
            fingers = self.Finger_Count()  # ✅ USE return value
        
            try:
                expected_digit = int(question[-1])
            except:
                expected_digit = -1
        
            if fingers is not None and fingers == expected_digit:
                self.label.setText("اجابه صحيحه!")
                play_audio_file(correct_path)
                self.score += 1
            else:
                self.label.setText("اجابه خاطئه برجاء التركيز.")
                play_audio_file(false_number)
            serial_comm.send('d')
            self.current_question += 1
            QTimer.singleShot(3000, self.ask_question)
        else:
            QTimer.singleShot(1000, self.record_answer)
    def record_answer(self):
        answer = whisper_asr.transcribe_audio()
        if  answer.strip()== 'ترجمة نانسي قنقر':
            self.label.setText("لم اسمع ذلك بوضوح, برجاء الاعاده")
            play_audio_file('repeat.mp3')
            QTimer.singleShot(2000, self.ask_question)
            return

        self.label.setText("جاري التصحيح...")
        QApplication.processEvents()

        self.answer_to_check = answer
        self.start_identity_verification(attempts=5, rounds=3)
    def start_identity_verification(self, attempts=5, rounds=3):
        self.verification_attempts = attempts
        self.verification_rounds = rounds
        self.successful_identity = False
        self._verify_identity()

    def _verify_identity(self):
        
        if self.verification_attempts == 0:
            self.verification_rounds -= 1
            if self.successful_identity:
                self._start_check_emotion()
                return
            elif self.verification_rounds == 0:
                self.label.setText("لست نفس الشخص , انهاء الجلسه")
                QTimer.singleShot(2000, self.start_standby)
                return
            else:
                self.verification_attempts = 5  # ← restore original value, not 1
                self.successful_identity = False
                QTimer.singleShot(500, self._verify_identity)
                return
    
        # Camera frame capture
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            time.sleep(0.5)
    
        ret, frame_check = self.cap.read()
        if not ret:
            self.label.setText("Camera error during identity check.")
            QTimer.singleShot(2000, self.start_standby)
            return
    
        identity_check, _ = detect.detect_verify(frame_check, self.database)
        print(f"[IDENTITY CHECK] Attempt: {self.verification_attempts}, Round: {self.verification_rounds}")
        print(f"[IDENTITY CHECK] Result: {identity_check}, Expected: {self.identity}")
        if identity_check == self.identity:
            self.successful_identity = True
            self._start_check_emotion()
            return
    
        self.verification_attempts -= 1
        QTimer.singleShot(500, self._verify_identity)
    def _start_check_emotion(self):
        self.emotion_attempts = 5
        self.detected_emotion = "Unknown"
        self._check_emotion()

    def _check_emotion(self):
        if self.emotion_attempts <= 0:
            print("❗ Emotion detection failed — proceeding anyway.")
            self.detected_emotion = "unknown"
            self._finalize_answer_with_emotion()
            return
    
        ret, frame = self.cap.read()
        if ret:
            try:
                _, emotion = detect_emotions_in_frame(frame)
                print(f"[EMOTION] Detected: {emotion}")
                if emotion and len(emotion) > 0:
                    first_emotion = emotion[0]
                    if first_emotion and first_emotion.lower() != "unknown":
                        self.detected_emotion = first_emotion
                        self._finalize_answer_with_emotion()
                        return
            except Exception as e:
                print(f"[EMOTION ERROR] {e}")
    
        self.emotion_attempts -= 1
        QTimer.singleShot(500, self._check_emotion)

    def get_adult(self):
        adult_name = ""
        audio_thread = None
        last_audio_time = 0  # Time when last audio was played
    
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
    
        def play_adult_audio():
            play_audio_file(adult)  # should block until audio finishes
    
        while adult_name != "Nour Fares":
            current_time = time.time()
    
            # Only start audio if not playing and enough time has passed
            if (audio_thread is None or not audio_thread.is_alive()) and (current_time - last_audio_time > 5):
                audio_thread = threading.Thread(target=play_adult_audio)
                audio_thread.start()
                last_audio_time = current_time
    
            # Process camera frame
            ret, frame = self.cap.read()
            if not ret:
                self.label.setText("Camera error3.")
                self.video_timer.stop()
                return
    
            adult_name, annotated_frame = detect.detect_verify(frame, self.database)
    
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_img).scaled(self.label.width(), self.label.height()))
            QApplication.processEvents()
    
            time.sleep(0.05)  # Frame rate delay
    
        self.cap.release()
        self.cap = None
        QTimer.singleShot(5000, self.start_standby)
    def _finalize_answer_with_emotion(self):
        emotion = self.detected_emotion.lower()

        if emotion in [ 0]: #"happy"
            self.label.setText(f"Detected emotion: {emotion}. Getting an adult...")
            self.get_adult()
            QTimer.singleShot(5000, self.start_standby)
            return

        correct = qwen_ar.evaluate_answer(self.answers[self.current_question], self.answer_to_check)
        if correct =='1':
            self.label.setText("اجابه صحيحيه!")
            play_audio_file(correct_path)
            self.score += 1
        else:
            self.label.setText("اجابه خاطئه , برجاء التركيز.")
            play_audio_file(false_ques)

        self.current_question += 1
        QTimer.singleShot(3000, self.ask_question)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AIGUI()
    window.show()
    sys.exit(app.exec_())
