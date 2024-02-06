"""
fontx2 to c header converter

currently assumes itself to be used just for PETI.
"""

import argparse
from os import path

str_desc = """Automatically convert a single fontx2 font to a c header file.
"""

out_header = """#ifndef %s_H_
#define %s_H_

#pragma PERSISTENT(%s)
const char *%s[] = {
"""

out_footer = """};

#endif

"""

class Namespace(object):
    pass

def parse_args(namespace):
    parser = argparse.ArgumentParser(description=str_desc)

    parser.add_argument('-i', help="path to input file", action="store")
    parser.add_argument('-o', help="path to input directory", action="store")

    args = parser.parse_args()
    namespace.input_path = args.i
    filename = path.split(args.i)[1]
    namespace.array_name = filename.split(".")[0]
    namespace.output_path = path.join(args.o, namespace.array_name+".h")

    return namespace


def determine_character_bytes(width, height):
    bytes_width = int(width/8)
    if width % 8:
        bytes_width += 1
    character_length = bytes_width * int(height)

    return character_length


def get_font_dimensions(namespace):
    with open(namespace.input_path, "rb") as f:
        f.seek(14, 0)  # move to width
        namespace.width = int.from_bytes(f.read(1),'big')  # pull a single byte to get width
        namespace.height = int.from_bytes(f.read(1),'big')
        namespace.character_bytes = determine_character_bytes(namespace.width, namespace.height)
        
        print("I think this font is %s by %s with %s bytes" % (namespace.width, namespace.height, namespace.character_bytes))
    
    return namespace


def write_output(namespace):
    with open(namespace.input_path, "rb") as f_in:
        with open(namespace.output_path, "w") as f_out:
            f_out.write(out_header % (namespace.array_name.upper(),namespace.array_name.upper(), namespace.array_name, namespace.array_name))
            f_in.seek(17)
            for char_index in range(256):
                f_out.write("  \"")
                for char_byte in range(namespace.character_bytes):
                    this_byte = f_in.read(1)
                    out_bit = reverse_bits(int.from_bytes(this_byte, 'big'),8)
                    f_out.write("\\x%02X" % out_bit)
                comment = " /* 0x%x */" % char_index
                f_out.write("\",%s\n" % comment)
            f_out.write(out_footer)
      
            
def reverse_bits(n, no_of_bits):
    result = 0
    for i in range(no_of_bits):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result
    


if __name__ == '__main__':
    ns = Namespace()
    ns = parse_args(ns)
    ns = get_font_dimensions(ns)
    ns = write_output(ns)
    exit(0)
