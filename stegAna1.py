# Simple Stegenographic analysis
# Extract LSB from an image and write to a file for visual inspection.
# Output extracted messages to screen.

import sys, getopt
from PIL import Image
import numpy as np

scriptName = ''
pixelMask = 254
byteMask  = 1
stopFlag = '{END}'
verbose = False

def print_usage():
      print('Usage:')
      print(scriptName, ' -h -v -b <LSB bits> -i <infile> -o <outfile>')
      print()

def log(*args):
    if verbose:
        for a in args:
            print(a, end='')
        print("")

def characterCheck(v):
#    return True
    if (v == 32) or (48 <= v and v <= 122): # Return spaces and ASCII between 0 and z.
        return True
#    if 32 <= v and v <= 132: # Any printable character
#        return True
    return False

def extractLSB(inArray, outArray, noBits):
    log('img dimensions: ', inArray.shape[0], inArray.shape[1], inArray.shape[2])
    log('noBits: ', noBits)
    byteMask = pow(2, noBits) - 1
    rows = inArray.shape[0]
    cols = inArray.shape[1]
    colours = inArray.shape[2]
    s = 0 # position in character being extracted
    v = 0 # integer value of character being extracted
    msg = ""
    for row in range(rows):
        for col in range(cols):
            for colour in range(colours):
                outArray[row, col, colour] = inArray[row, col, colour] & byteMask
                v += (inArray[row, col, colour] & byteMask) << s
                s += noBits
                if s >= 8: # found end of character
                    if characterCheck(v): # Check for printable character
                        msg += chr(v) # Only collect printable charcters
                    v = 0
                    s = 0
    return msg

def main(argv):
    global verbose
    noBits = 1

    try:
        opts, args = getopt.getopt(argv,"hvb:i:o:",["bits=", "infile=","ofile="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-v"):
            verbose = True
        elif opt in ("-b", "--bits"):
            noBits = int(arg)
        elif opt in ("-i", "--ifile"):
            inputFileName = arg
        elif opt in ("-o", "--ofile"):
            outputFileName = arg
    
    print('Input file is: ', inputFileName)
    print('Output file is: ', outputFileName)

    log('noBits: ', noBits)
    log('pow(2, noBits) - 1: ', pow(2, noBits) - 1)
    byteMask = pow(2, noBits) - 1
    log('byteMask: ', byteMask)
    print('byte mask: ', format(byteMask, '08b'))

    print('Opening input image...')
    img = Image.open(inputFileName)
    log('Image size & format: ', img.size, img.format)

    img.load() 
    inArray = np.asarray(img).copy()
    outArray = inArray.copy()

    log('input array size: ', inArray.size)
    if inArray.size < 100:
        log('input array')
        log(inArray)
    
    print('Extracting ', noBits, ' LSB bits')
    print('Note: Only extracting printable characters...')
    msg = extractLSB(inArray, outArray, noBits)
    print('msg: ', msg)

    log('output array size: ', outArray.size)
    if outArray.size < 100:
        log('output array')
        log(outArray)

    outImg = Image.fromarray(outArray)
    print('Writing output...')
    outImg.save(outputFileName)    

print('::: start :::')
print()
scriptName = sys.argv[0]

if __name__ == "__main__":
    main(sys.argv[1:])

print()
print('::: end :::')