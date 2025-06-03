#!/usr/bin/env python3
"""
AI Script Generator - Voice to Code Demo
Records audio, sends to OpenAI Whisper, generates UV scripts with Claude, and runs them
Usage: uv run ai_script_generator.py
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic>=0.40.0",
#     "openai>=1.0.0",
#     "pyaudio>=0.2.11",
#     "numpy>=1.24.0",
# ]
# ///

import sys
import os
import subprocess
import tempfile
import wave
import threading
import time
from pathlib import Path
import anthropic
from openai import OpenAI
import pyaudio
import numpy as np

class AudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.frames = []
        
    def start_recording(self):
        """Start recording audio"""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        self.recording = True
        self.frames = []
        
        print("🎙️  Recording started! Press ENTER to stop...")
        
        # Record in a separate thread
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.start()
        
        # Wait for user input
        input()
        return self.stop_recording()
        
    def _record_audio(self):
        """Record audio in background thread"""
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
                
    def stop_recording(self):
        """Stop recording and save to file"""
        self.recording = False
        
        if hasattr(self, 'record_thread'):
            self.record_thread.join()
            
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
        if not self.frames:
            print("❌ No audio recorded!")
            return None
        
        try:
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            
            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            
            print("🔇 Recording stopped!")
            return temp_file.name
            
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None

def transcribe_audio(file_path):
    """Transcribe audio using OpenAI Whisper API"""
    print("🎯 Transcribing audio with OpenAI Whisper...")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Get your key from: https://platform.openai.com/api-keys")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        transcription_text = transcription.strip()
        print(f"📝 Transcription: '{transcription_text}'")
        return transcription_text
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        print("   Make sure your OPENAI_API_KEY is valid and you have credits")
        return None

def generate_script_with_claude(user_request):
    """Send request to Claude and get a UV-compatible script"""
    print("🤖 Generating script with Claude...")
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        print("   Get your key from: https://console.anthropic.com/")
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        system_prompt = """You are an expert Python programmer who creates UV-compatible one-shot scripts.

Given a user request, create a complete Python script that:
1. Uses the UV script format with proper dependencies in comments
2. Includes proper error handling and user feedback
3. Has clear progress indicators and helpful output
4. Is production-ready and follows best practices
5. Includes proper docstring with usage instructions

Format your response as a complete Python script starting with #!/usr/bin/env python3 and including the # /// script block for dependencies.

The script should be ready to run with: uv run script_name.py

Make the script robust, user-friendly, and well-documented."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Create a UV-compatible Python script that: {user_request}"
                        }
                    ]
                }
            ]
        )
        
        script_content = message.content[0].text
        print("✅ Script generated successfully!")
        return script_content
        
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        print("   Make sure your ANTHROPIC_API_KEY is valid")
        return None

def save_and_display_script(script_content, filename="generated_script.py"):
    """Save script to file and display it with syntax highlighting"""
    script_path = Path(filename)
    
    # Save script
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"💾 Script saved as: {script_path}")
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    # Display with syntax highlighting (try different tools)
    print("\n" + "="*60)
    print("📄 GENERATED SCRIPT:")
    print("="*60)
    
    # Try bat first, then pygments, then plain cat
    display_commands = [
        ["bat", "--style=numbers,changes", "--language=python", str(script_path)],
        ["pygmentize", "-l", "python", "-f", "terminal", str(script_path)],
        ["cat", "-n", str(script_path)],
        ["type", str(script_path)]  # Windows fallback
    ]
    
    displayed = False
    for cmd in display_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(result.stdout)
                displayed = True
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if not displayed:
        # Fallback: print with basic formatting
        print(script_content)
    
    print("="*60)
    return script_path

def ask_user_to_run(script_path):
    """Ask user if they want to run the generated script"""
    while True:
        choice = input(f"\n🚀 Run the script with 'uv run {script_path}'? (y/n/q): ").lower().strip()
        
        if choice in ['y', 'yes']:
            print(f"\n⚡ Running: uv run {script_path}")
            print("-" * 50)
            
            try:
                # Run the script with UV
                result = subprocess.run(
                    ["uv", "run", str(script_path)], 
                    text=True,
                    timeout=120  # 2 minute timeout
                )
                
                print("-" * 50)
                if result.returncode == 0:
                    print("✅ Script completed successfully!")
                else:
                    print(f"❌ Script exited with code: {result.returncode}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Script timed out after 2 minutes")
            except FileNotFoundError:
                print("❌ UV not found. Please install UV first:")
                print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
            except Exception as e:
                print(f"❌ Error running script: {e}")
            
            break
            
        elif choice in ['n', 'no']:
            print("👍 Script saved but not executed.")
            break
            
        elif choice in ['q', 'quit']:
            print("👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("Please enter 'y' (yes), 'n' (no), or 'q' (quit)")

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        print("⚠️  Missing API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print()
        print("Set them with:")
        if "OPENAI_API_KEY" in missing_keys:
            print("   export OPENAI_API_KEY='your-openai-key-here'")
            print("   Get OpenAI key: https://platform.openai.com/api-keys")
        if "ANTHROPIC_API_KEY" in missing_keys:
            print("   export ANTHROPIC_API_KEY='your-anthropic-key-here'")
            print("   Get Anthropic key: https://console.anthropic.com/")
        print()
        
        choice = input("Continue anyway? (y/n): ").lower().strip()
        return choice in ['y', 'yes']
    
    return True

def main():
    """Main application workflow"""
    print("🎙️  AI Script Generator - Voice to Code Demo")
    print("=" * 50)
    print("This demo shows how to create Python scripts using voice commands!")
    print()
    print("How it works:")
    print("1. 🎤 Record your voice describing what script you want")
    print("2. 🎯 OpenAI Whisper transcribes your audio to text")
    print("3. 🤖 Claude AI generates a complete UV-compatible Python script")
    print("4. 📄 View the generated script with syntax highlighting")
    print("5. ⚡ Run the script immediately with UV")
    print()
    
    # Check dependencies
    try:
        import anthropic
        import pyaudio
        from openai import OpenAI
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("UV will install dependencies automatically when you run the script")
        return
    
    # Check API keys
    if not check_api_keys():
        return
    
    try:
        # Step 1: Record audio
        print("\n🎙️  STEP 1: Record your request")
        print("Describe what Python script you want created...")
        print("Examples:")
        print("  - 'Create a script that downloads weather data for my city'")
        print("  - 'Make a tool that resizes all images in a folder'")
        print("  - 'Build a CSV analyzer that shows statistics'")
        print()
        
        recorder = AudioRecorder()
        audio_file = recorder.start_recording()
        
        if not audio_file:
            print("❌ Failed to record audio. Please try again.")
            return
        
        # Step 2: Transcribe audio
        print("\n🎯 STEP 2: Transcribe audio with OpenAI Whisper")
        user_request = transcribe_audio(audio_file)
        
        if not user_request:
            print("❌ Could not transcribe audio. Please try again.")
            return
        
        # Clean up audio file
        os.unlink(audio_file)
        
        # Step 3: Generate script with Claude
        print("\n🤖 STEP 3: Generate script with Claude AI")
        script_content = generate_script_with_claude(user_request)
        
        if not script_content:
            print("❌ Could not generate script. Please try again.")
            return
        
        # Step 4: Save and display script
        print("\n📄 STEP 4: Save and display script")
        script_path = save_and_display_script(script_content)
        
        # Step 5: Ask user to run script
        print("\n⚡ STEP 5: Run the generated script")
        ask_user_to_run(script_path)
        
        print("\n🎉 Demo completed!")
        print(f"📁 Your script is saved as: {script_path}")
        print("💡 You can run it again anytime with: uv run generated_script.py")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try again or check your setup.")

if __name__ == "__main__":
    main()
