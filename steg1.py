# Simple Stegenographic embedding
# Write a message using the LSB of the first 8 bytes of each 3 pixel RGB grouping
# Note: only works on images that have are least 3 pixels in width

from re import L
import sys, getopt
from PIL import Image
import numpy as np

scriptName = ''
pixelMask = 254
byteMask  = 1
stopFlag = '{END}'

def print_usage():
      print('Usage:')
      print(scriptName, ' -m <message> -i <infile> -o <outfile>')
      print()

def substitution_value(c):
    if   c == 'e': return '3'
    elif c == '3': return 'e'
    elif c == 'o': return '0'
    elif c == '0': return 'o'
    else:          return c

def calc_encoding(pixelColor, char, n):
    return (pixelColor & pixelMask) | ((ord(char) >> n) & byteMask)

def encode_pixel_colour(array, x, y, z, char, n):
#    print()
#    print('encode array:')
#    print(array)
#    print('x, y, z: ',x, y, z)
#    print('char: ', char)
#    print('char in bits: ', format(ord(char), '08b'))
#    print('n: ', n)
    array[x,y,z] = calc_encoding(array[x,y,z], char, n)

def encode_message(img, msg):
    row = 0 # position in row
    col = 0 # current row
    p = 0   # position in message
    print('encoding_message...')

    print('img.size: ', img.size) 
    print(img.dtype)
    print(img.shape)
    imgRows = img.shape[0]
    print('Image Rows: ', imgRows)
    imgCols = img.shape[1]
    print('Image Cols: ', imgCols)
    msg += stopFlag
    msgLen = len(msg)
    print('Message being encoded: ', msg)
    print('Message length: ', msgLen)

    # Loop around, going three pixels at a time. 
    # Each pixel contains three bytes for R G B. 
    # Use the first eight bytes for each of the eight bits in each character of the message
    # Set the least significant bit of each to the corresponding bit of the character being embedded
    # Ignore the 9th byte (the Blue of the third pixel). 
    # We could use it but that would just create complications.
    # Other implementation try to use this bit to indicate end of the message. 
    # I think this is too obvious so rely on a Stop Flag in the embedded message.
    while row < imgRows and p < msgLen:
#        print('Encoding round: Offset: ', row, col, ' RGB[]: ', img[row, col], msg[p])
        c8 = "{0:b}".format(ord(msg[p]))
        print('Encoding: ', msg[p], ": ", c8, " <|> ", c8[::-1])
        encode_pixel_colour(img, row, col+0, 0, msg[p], 0)
        encode_pixel_colour(img, row, col+0, 1, msg[p], 1)
        encode_pixel_colour(img, row, col+0, 2, msg[p], 2)
        encode_pixel_colour(img, row, col+1, 0, msg[p], 3)
        encode_pixel_colour(img, row, col+1, 1, msg[p], 4)
        encode_pixel_colour(img, row, col+1, 2, msg[p], 5)
        encode_pixel_colour(img, row, col+2, 0, msg[p], 6)
        encode_pixel_colour(img, row, col+2, 1, msg[p], 7)

        col += 3 # move along columns in hops of three
        p += 1   # move to next character in the message to be embedded
        if col+3 >= imgCols: # if there isn't enough room on rest of the row to embed a character
            row += 1         # Go to the next row
            col = 0          # Reset the column counter to start at the beginning of that row
    if img.size < 100:
        print('output array:')
        print(img)


def decode_message(img):
    str = "" # Initialise string being decoded.
    row = 0 # position in row
    col = 0 # current row
    print('decoding_message...')
    print('img.size: ', img.size) 
    print(img.dtype)
    print(img.shape)

    imgRows = img.shape[0]
    print('Image Rows: ', imgRows)
    imgCols = img.shape[1]
    print('Image Cols: ', imgCols)

    # Loop around. Jump three columns at a time,
    # going to the next row if we have reached the end of the row.
    while row < imgRows and str.endswith(stopFlag) == False:
        # Iterate until either we run of of rows OR we find the Stop Flag in the message.
        # print('Decoding round: Offset: ', row, col, ' RGB[]: ', img[row, col])
        v = 0 # initialise value to zero = 00000000
        v += (img[row, col+0, 0] & byteMask) << 0 # Take the first bit, put it in the 0th position in v
        v += (img[row, col+0, 1] & byteMask) << 1 # Take the first bit, put it in the 1st position in v
        v += (img[row, col+0, 2] & byteMask) << 2 # As above, going to the 2nd position, and so on...
        v += (img[row, col+1, 0] & byteMask) << 3
        v += (img[row, col+1, 1] & byteMask) << 4
        v += (img[row, col+1, 2] & byteMask) << 5
        v += (img[row, col+2, 0] & byteMask) << 6
        v += (img[row, col+2, 1] & byteMask) << 7

        str +=chr(v) # Convert v to a character and append to the developing string.
#        print('str is now: ', str)
        col += 3 # Move to next set of three pixels
        if col+3 >= imgCols: # If there is no more space on this row
            row += 1         # Move to next row AND
            col = 0          # Start at beginning of that row
    str = str[:-len(stopFlag)] # Once the message has been extracted, remove stop flag.
    return str

def main(argv):
    print(argv)
    message = ''
    inputFileName = ''
    outputFileName = ''
    mode=''
    try:
        opts, args = getopt.getopt(argv,"hvedm:i:o:",["msg=", "infile=","outfile="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i", "--infile"):
            inputFileName = arg
        elif opt in ("-m", "--msg"):
            message = arg
        elif opt in ("-e", "--enc"):
            mode = 'encode'
        elif opt in ("-d", "--msg"):
            mode = 'decode'
        elif opt in ("-o", "--outfile"):
            outputFileName = arg
    
    print('message is: ', message)
    print('Input file is: ', inputFileName)
    print('Output file is: ', outputFileName)

    # Open input image
    img = Image.open(inputFileName)
    # size of the image
    print('Image size & format: ', img.size, img.format)

    # Load image into memory
    img.load() 
    imgarr = np.asarray(img).copy()
    #print('Original image array:')
    #print(imgarr)

    if mode == 'encode':
        encode_message(imgarr, message)
        #print('encoded image array:')
        #print(imgarr)
        newimg = Image.fromarray(imgarr)
        newimg.save(outputFileName)
    elif mode == 'decode':
        s = decode_message(imgarr)
        print('Decoded messages is: ', s)
        outFile = open(outputFileName, 'w')
        print('Writing contents to output file...')
        print(s, file=outFile)
        outFile.close()


print('::: start :::')
print()
scriptName = sys.argv[0]

if __name__ == "__main__":
    main(sys.argv[1:])

print()
print('::: end :::')