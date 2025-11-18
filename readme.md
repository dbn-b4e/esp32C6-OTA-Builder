# ESP32 Zigbee OTA File Generator & Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Complete toolkit for...
Complete toolkit for generating and managing Zigbee OTA files for ESP32-C6/H2 devices, with full Zigbee2MQTT integration support.

## Features

- ✅ **Generate OTA files** compatible with Zigbee2MQTT
- ✅ **Parse and verify** existing OTA files
- ✅ **Two modes**: Zigbee spec compliant OR Espressif-compatible
- ✅ **No ESP-IDF required** - standalone Python script
- ✅ **Automatic SHA512** calculation for Z2M manifests
- ✅ **Safe parameters** - separate input/output, no accidental overwrites

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Creating OTA Files](#creating-ota-files)
  - [Parsing OTA Files](#parsing-ota-files)
- [Complete OTA Workflow with Zigbee2MQTT](#complete-ota-workflow-with-zigbee2mqtt)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## Installation

### Requirements

- Python 3.6+
- arduino-cli (for compiling ESP32 firmware)
- Home Assistant with Zigbee2MQTT (for OTA updates)

### Install the Script

```bash
# Create tools directory
mkdir -p ~/esp-tools
cd ~/esp-tools

# Copy zigbee_ota_generator.py to this directory
# (The script provided separately)

# Make executable
chmod +x zigbee_ota_generator.py

# Test installation
python3 zigbee_ota_generator.py --help
```

---

## Quick Start

### Generate an OTA file

```bash
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --espressif-compatible
```

### Parse/Verify an OTA file

```bash
python3 ~/esp-tools/zigbee_ota_generator.py parse build/firmware.ota
```

Output:
```
============================================================
📋 ZIGBEE OTA FILE INFORMATION
============================================================
Magic Number:      0x0BEEF11E ✅
Manufacturer Code: 0x1049 (4169)
Image Type:        0x0001 (1)
File Version:      0x00000001
Total File Size:   816,994 bytes
SHA512 (for Z2M):  abc123...
============================================================
✅ OTA file is valid!
============================================================
```

---

## Usage

### Creating OTA Files

#### Basic Usage (Espressif-compatible - RECOMMENDED)

```bash
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i <input.bin> \
  -o <output.ota> \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --espressif-compatible
```

#### Zigbee Spec Compliant Mode

```bash
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i <input.bin> \
  -o <output.ota> \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001
```

#### All Parameters

```bash
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000002 \
  --stack-version 0x0002 \
  --min-hardware-version 1 \
  --max-hardware-version 1 \
  --header-string "ESP32-C6 v0.0.2" \
  --espressif-compatible
```

### Parameters Explained

| Parameter | Description | Format | Example |
|-----------|-------------|--------|---------|
| `-i, --input` | Input binary file (.bin) | Path | `build/firmware.bin` |
| `-o, --output` | Output OTA file (.ota) | Path | `build/firmware.ota` |
| `--manufacturer-code` | Manufacturer ID | Hex/Dec | `0x1049` (Espressif) |
| `--image-type` | Image type identifier | Hex/Dec | `0x0001` |
| `--file-version` | Firmware version | Hex/Dec | `0x00000001` |
| `--stack-version` | Zigbee stack version | Hex/Dec | `0x0002` (default) |
| `--min-hardware-version` | Minimum HW version | Integer | `1` (default) |
| `--max-hardware-version` | Maximum HW version | Integer | `1` (default) |
| `--header-string` | Description string | String | `"ESP32-C6 OTA"` |
| `--espressif-compatible` | Use Espressif format | Flag | (recommended) |

### Parsing OTA Files

```bash
python3 ~/esp-tools/zigbee_ota_generator.py parse <file.ota>
```

This will display:
- File header information
- Manufacturer code and image type
- File version
- Hardware version compatibility
- SHA512 hash (for Z2M)
- Sub-element structure
- Format detection (Zigbee spec vs Espressif)

---

## Complete OTA Workflow with Zigbee2MQTT

### Overview

1. **Prepare** initial and update firmware
2. **Flash** initial version via USB
3. **Pair** device with Zigbee2MQTT
4. **Setup** OTA server and manifest
5. **Configure** Z2M to use your OTA server
6. **Update** firmware over-the-air

### Step 1: Prepare Firmware Versions

```bash
cd ~/your-project

# Compile initial version (v1)
arduino-cli compile --fqbn esp32:esp32:esp32c6 --output-dir build .

# Create OTA file for v1 (for reference)
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/ota_test.ino.bin \
  -o build/firmware_v1.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --header-string "ESP32-C6 v0.0.1" \
  --espressif-compatible

# Modify your code (add version identifier, new features, etc.)
# Then compile v2
arduino-cli compile --fqbn esp32:esp32:esp32c6 --output-dir build .

# Create OTA file for v2 (for OTA update)
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/ota_test.ino.bin \
  -o build/firmware_v2.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000002 \
  --header-string "ESP32-C6 v0.0.2" \
  --espressif-compatible

# Verify the OTA file
python3 ~/esp-tools/zigbee_ota_generator.py parse build/firmware_v2.ota
```

### Step 2: Flash Initial Firmware

```bash
# Find your USB port
ls /dev/cu.*

# Flash v1 to device
arduino-cli upload --fqbn esp32:esp32:esp32c6 --port /dev/cu.usbserial-XXXX

# Verify in serial monitor
arduino-cli monitor --port /dev/cu.usbserial-XXXX --config baudrate=115200
```

### Step 3: Pair with Zigbee2MQTT

1. Open **Home Assistant → Zigbee2MQTT**
2. Click **"Permit join"** (150 seconds)
3. **Reset your ESP32** (hold BOOT button for 3+ seconds)
4. Wait for device to appear in Z2M
5. Note the device name/ID

### Step 4: Setup OTA Server

```bash
# Create OTA server directory
mkdir -p build/ota_server
cp build/firmware_v2.ota build/ota_server/

cd build/ota_server

# Get your Mac's IP address
IP=$(ipconfig getifaddr en0)  # WiFi
# OR
IP=$(ipconfig getifaddr en1)  # Ethernet

echo "Your IP: $IP"

# Calculate SHA512 and file size
SHA512=$(shasum -a 512 firmware_v2.ota | cut -d' ' -f1)
SIZE=$(stat -f%z firmware_v2.ota)

# Create Z2M manifest
cat > index.json << EOF
[
  {
    "modelId": "ESP32C6.OTATest",
    "manufacturerName": ["Espressif"],
    "imageType": 1,
    "fileVersion": 2,
    "fileSize": $SIZE,
    "sha512": "$SHA512",
    "url": "http://$IP:8000/firmware_v2.ota"
  }
]
EOF

echo "✅ Manifest created!"
cat index.json
```

### Step 5: Start OTA Server

```bash
cd build/ota_server

# Start HTTP server
python3 -m http.server 8000

# Verify accessibility in browser:
# http://YOUR_IP:8000/index.json
```

### Step 6: Configure Zigbee2MQTT

**In Home Assistant:**

1. Go to **Settings → Add-ons → Zigbee2MQTT → Configuration**
2. Add this at the top of the configuration file:

```yaml
ota:
  zigbee_ota_override_index_location: http://YOUR_IP:8000/index.json
```

3. **Save** and **restart** Zigbee2MQTT

### Step 7: Perform OTA Update

1. In **Zigbee2MQTT**, find your **ESP32-C6 device**
2. Go to the **"OTA" tab**
3. Click **"Check for updates"**
   - Should show: "Update available: v0.0.2"
4. Click **"Update"**
5. Wait (typically 5-10 minutes for ~800KB)
6. Monitor progress in Z2M logs

### Step 8: Verify Update

After the update completes:

```bash
# Reconnect serial monitor
arduino-cli monitor --port /dev/cu.usbserial-XXXX --config baudrate=115200

# You should now see the new version identifier
# "Firmware v0.0.2" 🎉
```

---

## Configuration

### Manufacturer Codes

Common manufacturer codes for reference:

| Manufacturer | Code (Hex) | Code (Dec) |
|--------------|------------|------------|
| Espressif | `0x1049` | 4169 |
| Philips | `0x100B` | 4107 |
| IKEA | `0x117C` | 4476 |
| Custom/Test | `0xFFFF` | 65535 |

### Image Types

Image type identifies the firmware purpose:

| Type | Description |
|------|-------------|
| `0x0000` | Manufacturer specific |
| `0x0001` | Standard firmware |
| `0x0002` | Bootloader |
| `0xFFFF` | Wild card |

### File Version Format

Version format: `0xAABBCCDD`

- `AA` - Major version
- `BB` - Minor version  
- `CC` - Patch version
- `DD` - Build number

Example: `0x01020304` = v1.2.3 build 4

---

## Troubleshooting

### OTA Update Not Starting

**Check 1: Verify manifest accessibility**
```bash
# In browser or curl
curl http://YOUR_IP:8000/index.json
```

**Check 2: Verify manufacturer code and image type**
- Must match what's configured in your ESP32 firmware
- Check with `parse` command

**Check 3: Z2M Configuration**
```yaml
# Must be in configuration.yaml
ota:
  zigbee_ota_override_index_location: http://YOUR_IP:8000/index.json
```

**Check 4: Z2M Logs**
- Look for OTA-related messages
- Check for connection errors to your server

### OTA Update Fails Mid-Transfer

**Common causes:**

1. **Network instability**
   - Ensure stable WiFi connection
   - Keep devices close to coordinator

2. **Server stopped**
   - Keep `python3 -m http.server 8000` running
   - Don't close the terminal

3. **Insufficient memory on ESP32**
   - Verify partition scheme supports OTA
   - Check available OTA partition size

4. **File corruption**
   - Regenerate OTA file
   - Verify with `parse` command
   - Check SHA512 matches

### Device Not Found in Z2M

**Steps:**

1. Verify Zigbee coordinator is working
2. Factory reset ESP32 (BOOT button 3+ seconds)
3. Enable permit join in Z2M
4. Reset ESP32 again
5. Wait 30 seconds

### Wrong Manufacturer Code

If you see errors about manufacturer mismatch:

```bash
# Check what's in your OTA file
python3 ~/esp-tools/zigbee_ota_generator.py parse build/firmware.ota

# Check what's configured in your ESP32 code
# Look for: zbLight.setManufacturerAndModel()
```

### File Size Mismatch

If Z2M reports size mismatch:

```bash
# Regenerate manifest with correct size
SIZE=$(stat -f%z firmware.ota)
echo "File size: $SIZE"

# Update index.json with correct size
```

---

## Examples

### Example 1: Simple OTA Update

```bash
# Compile firmware
arduino-cli compile --fqbn esp32:esp32:esp32c6 --output-dir build .

# Create OTA file
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --espressif-compatible

# Setup server
mkdir -p build/ota && cp build/firmware.ota build/ota/
cd build/ota
IP=$(ipconfig getifaddr en0)
SHA512=$(shasum -a 512 firmware.ota | cut -d' ' -f1)
SIZE=$(stat -f%z firmware.ota)

cat > index.json << EOF
[{
  "modelId": "ESP32C6.Light",
  "manufacturerName": ["Espressif"],
  "imageType": 1,
  "fileVersion": 1,
  "fileSize": $SIZE,
  "sha512": "$SHA512",
  "url": "http://$IP:8000/firmware.ota"
}]
EOF

# Start server
python3 -m http.server 8000
```

### Example 2: Multiple Versions

```bash
# Create v1, v2, v3
for ver in 1 2 3; do
  python3 ~/esp-tools/zigbee_ota_generator.py create \
    -i build/firmware.bin \
    -o build/firmware_v${ver}.ota \
    --manufacturer-code 0x1049 \
    --image-type 0x0001 \
    --file-version 0x0000000${ver} \
    --header-string "ESP32-C6 v0.0.${ver}" \
    --espressif-compatible
done
```

### Example 3: Automated Workflow Script

```bash
#!/bin/bash
# save as: ota_build.sh

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

# Compile
arduino-cli compile --fqbn esp32:esp32:esp32c6 --output-dir build .

# Create OTA
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware_v${VERSION}.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x000000$(printf "%02d" $VERSION) \
  --header-string "ESP32-C6 v0.0.${VERSION}" \
  --espressif-compatible

# Parse
python3 ~/esp-tools/zigbee_ota_generator.py parse build/firmware_v${VERSION}.ota

echo "✅ OTA v${VERSION} ready!"
```

Usage:
```bash
chmod +x ota_build.sh
./ota_build.sh 5  # Creates version 5
```

### Example 4: Different Hardware Versions

```bash
# For hardware v1
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware_hw1.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --min-hardware-version 1 \
  --max-hardware-version 1 \
  --espressif-compatible

# For hardware v2
python3 ~/esp-tools/zigbee_ota_generator.py create \
  -i build/firmware.bin \
  -o build/firmware_hw2.ota \
  --manufacturer-code 0x1049 \
  --image-type 0x0001 \
  --file-version 0x00000001 \
  --min-hardware-version 2 \
  --max-hardware-version 2 \
  --espressif-compatible
```

---

## ESP32 Firmware Template

Add this to your Arduino sketch for OTA support:

```cpp
#include "Zigbee.h"
#include "ep/ZigbeeLight.h"

// OTA Configuration
#define OTA_UPGRADE_RUNNING_FILE_VERSION    0x00000001
#define OTA_UPGRADE_DOWNLOADED_FILE_VERSION 0x00000002
#define OTA_UPGRADE_HW_VERSION              0x0001
#define OTA_UPGRADE_MANUFACTURER            0x1049
#define OTA_UPGRADE_IMAGE_TYPE              0x0001

ZigbeeLight zbLight = ZigbeeLight(10);

void setup() {
  Serial.begin(115200);
  Serial.println("Firmware v0.0.1");  // Version identifier
  
  // Configure device
  zbLight.setManufacturerAndModel("Espressif", "ESP32C6.Light");
  zbLight.setPowerSource(ZB_POWER_SOURCE_MAINS);
  
  // Enable OTA client
  zbLight.addOTAClient(
    OTA_UPGRADE_RUNNING_FILE_VERSION,
    OTA_UPGRADE_DOWNLOADED_FILE_VERSION,
    OTA_UPGRADE_HW_VERSION
  );
  
  // Optional: OTA progress callback
  zbLight.onOtaUpdate([](uint8_t progress) {
    Serial.printf("OTA Progress: %d%%\n", progress);
  });
  
  // Start Zigbee
  Zigbee.addEndpoint(&zbLight);
  Zigbee.begin(ZIGBEE_END_DEVICE);
  
  // Wait for connection
  while (!Zigbee.connected()) {
    delay(100);
  }
  Serial.println("Connected to Zigbee network");
  
  // Optional: Request OTA check at startup
  zbLight.requestOTAUpdate();
}

void loop() {
  delay(1000);
}
```

---

## Advanced Topics

### Two Formats Explained

**Zigbee Spec Compliant (default):**
- "Total Image Size" = Sub-element headers + Firmware
- Strictly follows ZCL specification
- Padding with `0xFF`

**Espressif-Compatible (`--espressif-compatible`):**
- "Total Image Size" = Header + Sub-element headers + Firmware
- Matches Espressif's `image_builder_tool.py` behavior
- Padding with `0x00`
- **Recommended for ESP32 projects**

### SHA512 Calculation

Z2M uses SHA512 to verify file integrity:

```bash
# Manual calculation
shasum -a 512 firmware.ota

# Script does this automatically during parse
python3 ~/esp-tools/zigbee_ota_generator.py parse firmware.ota
```

### Serving OTA Files

**Method 1: Simple HTTP Server (Development)**
```bash
cd build/ota_server
python3 -m http.server 8000
```

**Method 2: Nginx (Production)**
```nginx
server {
    listen 8000;
    server_name _;
    root /path/to/ota_server;
    
    location / {
        add_header Access-Control-Allow-Origin *;
    }
}
```

**Method 3: Home Assistant Add-on**
- Use File Editor add-on
- Place files in `/config/www/ota/`
- Access via `http://homeassistant.local:8123/local/ota/`

---

## Resources

- [Zigbee OTA Specification (ZCL)](https://zigbeealliance.org/wp-content/uploads/2019/12/07-5123-08-Zigbee-Cluster-Library.pdf)
- [ESP32 Zigbee SDK](https://github.com/espressif/esp-zigbee-sdk)
- [Zigbee2MQTT OTA Guide](https://www.zigbee2mqtt.io/guide/usage/ota_updates.html)
- [Espressif Documentation](https://docs.espressif.com/projects/esp-zigbee-sdk/)

---

## License

This tool is provided as-is for use with ESP32 Zigbee development.

---

## Credits

Developed for ESP32-C6/H2 Zigbee OTA workflows with Zigbee2MQTT integration.

Zigbee OTA format based on Zigbee Cluster Library Specification (ZCL 07-5123-08).

---

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [Examples](#examples)
- Verify file with `parse` command
- Check Z2M logs for detailed error messages

**Happy OTA updating! 🚀**
