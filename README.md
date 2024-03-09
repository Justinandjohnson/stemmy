🎤 Demucs Vocal Isolation App 🎶
Welcome to the world of crystal-clear vocals with the Demucs Vocal Isolation App! Are you ready to isolate vocals like a pro? 🌟 This app is here to transform your audio experience, whether you're a budding musician, a passionate vocalist, or just someone who loves playing with sound! 🎧

Features 🚀
- Start Recording: Hit the record button and capture your voice or any sound, straight from your device's microphone. 🎙️
- Play Beat: Jam along with your favorite beats while recording. Just tap and get into the groove! 🥁
- Isolate Vocals: With just a click, our state-of-the-art Demucs model separates vocals from any audio track. Experience the magic! ✨
- Upload and Process: Got an existing audio file? Upload it and let our app work its magic. 📤
- Save Separated Stems: After isolating, save the pristine vocals as a new audio file. Perfect for remixes and samples! 🎚️
- Real-Time Audio Levels: Keep an eye on your recording levels with our dynamic audio level meter. 📊

Getting Started 🌈
1. Install Dependencies:
   - Make sure you have Python 3.8 or higher installed.
   - Install the project dependencies:
     ```
     python3 -m pip install -U demucs
     ```
     or for the bleeding-edge version:
     ```
     python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs
     ```
   - (Optional for developers) Set up the environment for model training and development:
     ```
     conda env update -f environment-cpu.yml  # For CPU
     conda env update -f environment-cuda.yml # For GPU
     conda activate demucs
     pip install -e .
     ```

2. Download the Demucs v4 model:
   - Get the Demucs v4 model from [this link](https://github.com/adefossez/demucs).
   - Add it to the project's model directory and ensure your folder paths are set correctly in the code.

3. Run the App:
   - Launch `voxtest.py` and watch the interface come alive.
   - Select your recording device from the drop-down menu.
   - Start creating and isolating vocals in a user-friendly environment!

Requirements 📋
- Python 3.8 or higher
- Demucs v4 model (downloadable from [here](https://github.com/adefossez/demucs))
- SoundDevice, PyQT5, Torch, Torchaudio, Numpy
- A microphone for recording 📼
- Or A recording from your iPhone
- Enthusiasm for sound! 🎸

Interface Sneak-Peek 🖥️
Imagine a sleek, intuitive interface with cool background graphics that gets you in the mood for some audio fun. That's what Demucs Vocal Isolation App is all about!

Contribute and Feedback 💌
Got ideas or feedback? We'd love to hear from you! Help us make this app even better. Fork the repository, make your changes, and submit a pull request.

License 📜
This project is open-source and available under the MIT License.
