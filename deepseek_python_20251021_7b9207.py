#!/usr/bin/env python3
import requests
import os
import time
import subprocess
import sys
from urllib.parse import urlparse

class AllInOneStreamTool:
    def __init__(self):
        self.m3u8_url = "https://het100a.4rouwanda-shop.store/live/69854211/index.m3u8"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def download_segments(self, count=20):
        print("📥 Downloading segments...")
        try:
            r = self.session.get(self.m3u8_url, timeout=10)
            segments = [line for line in r.text.split('\n') if line.startswith('http')]
            print(f"Found {len(segments)} segments")
            
            for i, url in enumerate(segments[:count]):
                try:
                    print(f"Downloading segment {i+1}/{count}...")
                    r = self.session.get(url, timeout=30)
                    with open(f"segment_{i:03d}.ts", 'wb') as f:
                        f.write(r.content)
                    print(f"✅ Saved segment_{i:03d}.ts")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"❌ Failed segment {i}: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def record_stream(self, duration=60, output="output.mp4"):
        print(f"🎥 Recording {duration}s to {output}...")
        try:
            cmd = ['ffmpeg', '-i', self.m3u8_url, '-t', str(duration), '-c', 'copy', output, '-y']
            subprocess.run(cmd, check=True)
            print(f"✅ Saved to {output}")
        except Exception as e:
            print(f"❌ FFmpeg error: {e}")
    
    def play_stream(self):
        print("▶️ Playing stream...")
        try:
            cmd = ['ffplay', '-i', self.m3u8_url, '-window_title', 'HLS Stream']
            subprocess.run(cmd)
        except Exception as e:
            print(f"❌ FFplay error: {e}")
    
    def stream_info(self):
        print("🔍 Getting stream info...")
        try:
            r = self.session.get(self.m3u8_url, timeout=10)
            print("=== M3U8 CONTENT ===")
            print(r.text)
            print("=== SEGMENT URLs ===")
            segments = [line for line in r.text.split('\n') if line.startswith('http')]
            for url in segments[:5]:
                print(url)
            if len(segments) > 5:
                print(f"... and {len(segments)-5} more")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def monitor_stream(self):
        print("👀 Monitoring stream (Ctrl+C to stop)...")
        last_content = ""
        try:
            while True:
                try:
                    r = self.session.get(self.m3u8_url, timeout=5)
                    if r.text != last_content:
                        segments = [line for line in r.text.split('\n') if line.startswith('http')]
                        print(f"[{time.strftime('%H:%M:%S')}] Playlist updated - {len(segments)} segments")
                        last_content = r.text
                    time.sleep(10)
                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
                    time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    tool = AllInOneStreamTool()
    
    print("🚀 HLS Stream Tool for Termux")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Command line mode
        cmd = sys.argv[1]
        if cmd == "download":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            tool.download_segments(count)
        elif cmd == "record":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            output = sys.argv[3] if len(sys.argv) > 3 else "output.mp4"
            tool.record_stream(duration, output)
        elif cmd == "play":
            tool.play_stream()
        elif cmd == "info":
            tool.stream_info()
        elif cmd == "monitor":
            tool.monitor_stream()
        else:
            print_help()
    else:
        # Interactive mode
        while True:
            print("\n📋 Menu:")
            print("1. Download segments")
            print("2. Record stream")
            print("3. Play stream")
            print("4. Stream info")
            print("5. Monitor stream")
            print("6. Exit")
            
            choice = input("\nChoose option (1-6): ").strip()
            
            if choice == "1":
                count = input("How many segments? (default 20): ").strip()
                count = int(count) if count.isdigit() else 20
                tool.download_segments(count)
            elif choice == "2":
                duration = input("Duration in seconds? (default 60): ").strip()
                duration = int(duration) if duration.isdigit() else 60
                output = input("Output filename? (default output.mp4): ").strip() or "output.mp4"
                tool.record_stream(duration, output)
            elif choice == "3":
                tool.play_stream()
            elif choice == "4":
                tool.stream_info()
            elif choice == "5":
                tool.monitor_stream()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")

def print_help():
    print("Usage:")
    print("  python3 stream.py download [count]")
    print("  python3 stream.py record [duration] [output]")
    print("  python3 stream.py play")
    print("  python3 stream.py info")
    print("  python3 stream.py monitor")
    print("\nExamples:")
    print("  python3 stream.py download 10")
    print("  python3 stream.py record 30 video.mp4")
    print("  python3 stream.py play")

if __name__ == "__main__":
    main()