import os
import sys
import zipfile
import shutil
import urllib.request
import urllib.parse

DOWNLOAD_DIR = os.path.expanduser("~/.cache/stm32-tools")
INSTALL_DIR = os.path.expanduser("~/.local/stm32-tools")

TOOLS = [
    {
        "name": "arm-gcc",
        "url": "https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi.zip",
        "extract_dir": "arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi",
        "bin_path": "bin",
        "check_file": "arm-none-eabi-gcc.exe"
    },
    {
        "name": "cmake",
        "url": "https://github.com/Kitware/CMake/releases/download/v3.30.1/cmake-3.30.1-windows-x86_64.zip",
        "extract_dir": "cmake-3.30.1-windows-x86_64",
        "bin_path": "bin",
        "check_file": "cmake.exe"
    },
    {
        "name": "ninja",
        "url": "https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-win.zip",
        "extract_dir": "ninja-win",
        "bin_path": "",
        "check_file": "ninja.exe"
    },
    {
        "name": "openocd",
        "url": "https://github.com/xpack-dev-tools/openocd-xpack/releases/download/v0.12.0-4/xpack-openocd-0.12.0-4-win32-x64.zip",
        "extract_dir": "xpack-openocd-0.12.0-4",
        "bin_path": "bin",
        "check_file": "openocd.exe"
    }
]

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
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

def extract_zip(zip_path, dest_dir):
    print(f"Extracting {zip_path} to {dest_dir}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        print("Extraction complete")
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def install_tool(tool):
    tool_name = tool["name"]
    url = tool["url"]
    extract_dir = tool["extract_dir"]
    bin_path = tool["bin_path"]
    check_file = tool["check_file"]
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    zip_filename = os.path.basename(url)
    zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)
    
    if os.path.exists(zip_path):
        print(f"File already exists: {zip_path}")
    else:
        if not download_file(url, zip_path):
            return False
    
    tool_install_dir = os.path.join(INSTALL_DIR, tool_name)
    if os.path.exists(tool_install_dir):
        shutil.rmtree(tool_install_dir)
    
    extract_dest = os.path.join(INSTALL_DIR, f"{tool_name}-temp")
    if os.path.exists(extract_dest):
        shutil.rmtree(extract_dest)
    
    if not extract_zip(zip_path, extract_dest):
        return False
    
    extracted_full = os.path.join(extract_dest, extract_dir)
    if os.path.exists(extracted_full):
        shutil.move(extracted_full, tool_install_dir)
    else:
        print(f"Warning: Expected directory not found: {extracted_full}")
        contents = os.listdir(extract_dest)
        print(f"Contents of extract_dest: {contents}")
        if contents:
            shutil.move(os.path.join(extract_dest, contents[0]), tool_install_dir)
    
    shutil.rmtree(extract_dest, ignore_errors=True)
    
    if bin_path:
        check_path = os.path.join(tool_install_dir, bin_path, check_file)
    else:
        check_path = os.path.join(tool_install_dir, check_file)
    
    if os.path.exists(check_path):
        print(f"✓ {tool_name} installed successfully")
        return os.path.join(tool_install_dir, bin_path) if bin_path else tool_install_dir
    else:
        print(f"✗ {tool_name} installation verification failed")
        return False

def get_path_entries():
    entries = []
    for tool in TOOLS:
        tool_install_dir = os.path.join(INSTALL_DIR, tool["name"])
        if tool["bin_path"]:
            bin_dir = os.path.join(tool_install_dir, tool["bin_path"])
        else:
            bin_dir = tool_install_dir
        
        if os.path.exists(os.path.join(bin_dir, tool["check_file"])):
            entries.append(bin_dir)
    return entries

def generate_env_script():
    entries = get_path_entries()
    if not entries:
        print("No tools found to configure")
        return
    
    script_path = os.path.join(INSTALL_DIR, "setup_env.bat")
    with open(script_path, "w") as f:
        f.write("@echo off\n")
        f.write("echo Setting up STM32 development environment...\n")
        for entry in entries:
            f.write(f'set "PATH={entry};%PATH%"\n')
        f.write("echo Environment setup complete.\n")
        f.write("echo Available tools:\n")
        f.write("arm-none-eabi-gcc --version\n")
        f.write("cmake --version\n")
        f.write("ninja --version\n")
        f.write("openocd --version\n")
    
    print(f"Environment setup script generated: {script_path}")
    return script_path

def main():
    print("=" * 60)
    print("STM32 Development Tools Installer")
    print("=" * 60)
    
    installed_paths = []
    for tool in TOOLS:
        print(f"\n--- Installing {tool['name']} ---")
        path = install_tool(tool)
        if path:
            installed_paths.append(path)
    
    if installed_paths:
        print("\n" + "=" * 60)
        print("Installation Summary")
        print("=" * 60)
        for i, path in enumerate(installed_paths):
            print(f"{i+1}. {TOOLS[i]['name']}: {path}")
        
        generate_env_script()
        
        print("\n" + "=" * 60)
        print("To use these tools, run:")
        print(f"  {os.path.join(INSTALL_DIR, 'setup_env.bat')}")
        print("or add the following paths to your system PATH:")
        for path in installed_paths:
            print(f"  {path}")
        print("=" * 60)
    else:
        print("\nInstallation failed. Please check network connectivity.")

if __name__ == "__main__":
    main()