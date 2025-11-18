#!/usr/bin/env python3
"""
Zigbee OTA File Generator & Parser
Supports both standard Zigbee spec and Espressif-compatible modes
"""

import struct
import hashlib
import argparse
import sys
from pathlib import Path

class ZigbeeOTAGenerator:
    MAGIC_NUMBER = 0x0BEEF11E
    HEADER_VERSION = 0x0100
    HEADER_LENGTH_EXTENDED = 60
    TAG_UPGRADE_IMAGE = 0x0000
    FIELD_CONTROL_HW_VERSION = 0x0004
    
    def generate_ota_file(self, args):
        """Generate Zigbee OTA file"""
        
        with open(args.input, 'rb') as f:
            firmware_data = f.read()
        
        firmware_size = len(firmware_data)
        
        print(f"📦 Input binary: {args.input}")
        print(f"   Size: {firmware_size:,} bytes")
        
        # Header string padding
        header_string = args.header_string.encode('utf-8')[:32]
        if args.espressif_compatible:
            # Espressif pads with 0x00
            header_string = header_string.ljust(32, b'\x00')
            print(f"   Mode: Espressif-compatible")
        else:
            # Zigbee spec recommends 0xFF
            header_string = header_string.ljust(32, b'\xFF')
            print(f"   Mode: Zigbee spec compliant")
        
        # Calculate Total Image Size
        subelement_header_size = 6
        
        if args.espressif_compatible:
            # Espressif includes header in Total Image Size
            total_image_size = self.HEADER_LENGTH_EXTENDED + subelement_header_size + firmware_size
        else:
            # Zigbee spec: Total Image Size = everything AFTER the header
            total_image_size = subelement_header_size + firmware_size
        
        # Build OTA header (60 bytes)
        header = struct.pack(
            '<I H H H H H I H 32s I H H',
            self.MAGIC_NUMBER,
            self.HEADER_VERSION,
            self.HEADER_LENGTH_EXTENDED,
            self.FIELD_CONTROL_HW_VERSION,
            args.manufacturer_code,
            args.image_type,
            args.file_version,
            args.stack_version,
            header_string,
            total_image_size,
            args.min_hardware_version,
            args.max_hardware_version
        )
        
        # Sub-element header (6 bytes)
        subelement_header = struct.pack('<H I', self.TAG_UPGRADE_IMAGE, firmware_size)
        
        # Assemble
        ota_data = header + subelement_header + firmware_data
        
        with open(args.output, 'wb') as f:
            f.write(ota_data)
        
        sha512 = hashlib.sha512(ota_data).hexdigest()
        
        print(f"\n✅ OTA file generated: {args.output}")
        print(f"   Header: {len(header)} bytes")
        print(f"   Total Image Size field: {total_image_size:,} bytes")
        print(f"   Actual OTA file size: {len(ota_data):,} bytes")
        print(f"   SHA512: {sha512}")
        
        return True
    
    def parse_ota_file(self, filename):
        """Parse OTA file"""
        
        with open(filename, 'rb') as f:
            data = f.read()
        
        if len(data) < 56:
            print("❌ File too small")
            return False
        
        basic = struct.unpack('<I H H H H H I H 32s I', data[:56])
        magic, hdr_ver, hdr_len, field_ctrl, manuf, img_type, \
        file_ver, stack_ver, hdr_str, img_size = basic
        
        if magic != self.MAGIC_NUMBER:
            print(f"❌ Invalid magic: 0x{magic:08X}")
            return False
        
        hdr_str_clean = hdr_str.rstrip(b'\x00\xFF').decode('utf-8', errors='ignore')
        
        has_hw = (field_ctrl & self.FIELD_CONTROL_HW_VERSION) != 0
        min_hw, max_hw = None, None
        
        if has_hw and hdr_len >= 60:
            hw_vers = struct.unpack('<H H', data[56:60])
            min_hw, max_hw = hw_vers
        
        print("\n" + "="*60)
        print("📋 ZIGBEE OTA FILE INFORMATION")
        print("="*60)
        print(f"Magic Number:      0x{magic:08X} ✅")
        print(f"Header Version:    0x{hdr_ver:04X}")
        print(f"Header Length:     {hdr_len} bytes" + (" (Extended)" if hdr_len > 56 else ""))
        print(f"Field Control:     0x{field_ctrl:04X}")
        print(f"Manufacturer Code: 0x{manuf:04X} ({manuf})")
        print(f"Image Type:        0x{img_type:04X} ({img_type})")
        print(f"File Version:      0x{file_ver:08X}")
        print(f"Stack Version:     0x{stack_ver:04X}")
        print(f"Header String:     '{hdr_str_clean}'")
        print(f"Total Image Size:  {img_size:,} bytes (in header)")
        
        if has_hw and min_hw is not None:
            print(f"Min HW Version:    {min_hw}")
            print(f"Max HW Version:    {max_hw}")
        
        print(f"Total File Size:   {len(data):,} bytes")
        
        # Detect mode
        expected_zigbee_spec = (len(data) - hdr_len)
        expected_espressif = len(data)
        
        if img_size == expected_espressif:
            print(f"Format detected:   Espressif-style (includes header)")
        elif img_size == expected_zigbee_spec:
            print(f"Format detected:   Zigbee spec compliant")
        else:
            print(f"Format detected:   Non-standard")
        
        sha512 = hashlib.sha512(data).hexdigest()
        print(f"\nSHA512 (for Z2M):  {sha512}")
        
        print(f"\n📦 SUB-ELEMENTS:")
        offset = hdr_len
        
        while offset + 6 <= len(data):
            tag_id, tag_len = struct.unpack('<H I', data[offset:offset+6])
            
            tag_names = {
                0x0000: "Upgrade Image",
                0x0001: "ECDSA Signature",
                0x0002: "ECDSA Certificate"
            }
            tag_name = tag_names.get(tag_id, f"Unknown (0x{tag_id:04X})")
            
            print(f"   • {tag_name} (Tag 0x{tag_id:04X})")
            print(f"     Length: {tag_len:,} bytes")
            
            offset += 6 + tag_len
            if offset > len(data):
                break
        
        print("="*60)
        print("✅ OTA file is valid!")
        print("="*60 + "\n")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Zigbee OTA File Generator & Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create OTA (Zigbee spec compliant):
    %(prog)s create -i firmware.bin -o firmware.ota \\
      --manufacturer-code 0x1049 --image-type 0x0001 \\
      --file-version 0x00000002
  
  Create OTA (Espressif-compatible):
    %(prog)s create -i firmware.bin -o firmware.ota \\
      --manufacturer-code 0x1049 --image-type 0x0001 \\
      --file-version 0x00000002 --espressif-compatible
  
  Parse OTA file:
    %(prog)s parse firmware.ota
        """
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Create command
    create = subparsers.add_parser('create', help='Create OTA file')
    create.add_argument('-i', '--input', required=True, help='Input .bin file')
    create.add_argument('-o', '--output', required=True, help='Output .ota file')
    create.add_argument('--manufacturer-code', type=lambda x: int(x, 0), required=True)
    create.add_argument('--image-type', type=lambda x: int(x, 0), required=True)
    create.add_argument('--file-version', type=lambda x: int(x, 0), required=True)
    create.add_argument('--stack-version', type=lambda x: int(x, 0), default=0x0002)
    create.add_argument('--min-hardware-version', type=lambda x: int(x, 0), default=1)
    create.add_argument('--max-hardware-version', type=lambda x: int(x, 0), default=1)
    create.add_argument('--header-string', default='ESP32 Zigbee OTA')
    create.add_argument('--espressif-compatible', action='store_true',
                       help='Use Espressif-compatible format (includes header in Total Image Size)')
    
    # Parse command
    parse = subparsers.add_parser('parse', help='Parse OTA file')
    parse.add_argument('file', help='OTA file to parse')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    gen = ZigbeeOTAGenerator()
    
    if args.command == 'create':
        if not Path(args.input).exists():
            print(f"❌ Input not found: {args.input}")
            return 1
        return 0 if gen.generate_ota_file(args) else 1
    
    elif args.command == 'parse':
        if not Path(args.file).exists():
            print(f"❌ File not found: {args.file}")
            return 1
        return 0 if gen.parse_ota_file(args.file) else 1

if __name__ == '__main__':
    sys.exit(main())
