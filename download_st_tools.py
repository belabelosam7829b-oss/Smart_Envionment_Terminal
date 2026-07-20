import os
import sys
import urllib.request
import ssl

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "tools")

TOOLS = [
    {
        "name": "ST-Link Driver (GitHub Mirror)",
        "url": "https://github.com/texane/stlink/releases/download/v1.8.0/stlink-1.8.0-x86_64-w64-mingw32.zip",
        "filename": "stlink-1.8.0.zip"
    },
    {
        "name": "OpenOCD ST-Link config",
        "url": "https://raw.githubusercontent.com/openocd-org/openocd/master/tcl/interface/stlink.cfg",
        "filename": "stlink.cfg"
    },
    {
        "name": "OpenOCD STM32F1 config",
        "url": "https://raw.githubusercontent.com/openocd-org/openocd/master/tcl/target/stm32f1x.cfg",
        "filename": "stm32f1x.cfg"
    }
]

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, dest_path, reporthook=progress_hook)
        print(f"Download complete: {dest_path}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def progress_hook(count, block_size, total_size):
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rProgress: {percent}%")
        sys.stdout.flush()

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    for tool in TOOLS:
        print(f"\n--- Downloading {tool['name']} ---")
        dest_path = os.path.join(DOWNLOAD_DIR, tool["filename"])
        
        if os.path.exists(dest_path):
            print(f"File already exists: {dest_path}")
        else:
            download_file(tool["url"], dest_path)
    
    print(f"\nDownloads saved to: {DOWNLOAD_DIR}")
    
    print("\n" + "=" * 60)
    print("STM32CubeProgrammer Manual Download")
    print("=" * 60)
    print("Please manually download from ST official website:")
    print("https://www.st.com/en/development-tools/stm32cubeprog.html")
    print("\nST-Link USB Driver Manual Download:")
    print("https://www.st.com/en/development-tools/stsw-link009.html")
    print("=" * 60)

if __name__ == "__main__":
    main()