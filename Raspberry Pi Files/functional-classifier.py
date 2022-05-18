#!/usr/bin/python3

# ****************************************************************************
# Copyright(c) 2017 Intel Corporation. 
# License: MIT See LICENSE file in root directory.
# ****************************************************************************

# How to classify images using DNNs on Intel Neural Compute Stick (NCS)

import os
import sys
import numpy
import ntpath
import argparse
import skimage.io
import skimage.transform
import picamera
import mvnc.mvncapi as mvnc
import serial
import time
import subprocess

#time.sleep(5)
imageFile = "/home/pi/workspace/ncappzoo/apps/image-classifier/newimage.jpg"
# Number of top prodictions to print
NUM_PREDICTIONS      = 2

# Variable to store commandline arguments
ARGS                 = None

process = subprocess.call('sudo rfcomm connect hci0 98:D3:31:FC:7F:99 1 &', shell=True)
while 1:
    try:
        ser = serial.Serial(port='/dev/rfcomm0', baudrate=9600)
        print("port is open")
        break
    except:
        pass

# ---- Step 1: Open the enumerated device and get a handle to it -------------

def open_ncs_device():

    # Look for enumerated NCS device(s); quit program if none found.
    devices = mvnc.EnumerateDevices()
    if len( devices ) == 0:
        print( "No devices found" )
        quit()

    # Get a handle to the first enumerated device and open it
    device = mvnc.Device( devices[0] )
    device.OpenDevice()

    return device

# ---- Step 2: Load a graph file onto the NCS device -------------------------

def load_graph( device ):

    # Read the graph file into a buffer
    with open( ARGS.graph, mode='rb' ) as f:
        blob = f.read()

    # Load the graph buffer into the NCS
    graph = device.AllocateGraph( blob )

    return graph

# ---- Step 3: Pre-process the images ----------------------------------------

def pre_process_image( img_draw ):

    # Resize image [Image size is defined during training]
    img = skimage.transform.resize( img_draw, ARGS.dim, preserve_range=True )

    # Convert RGB to BGR [skimage reads image in RGB, some networks may need BGR]
    if( ARGS.colormode == "bgr" ):
        img = img[:, :, ::-1]

    # Mean subtraction & scaling [A common technique used to center the data]
    img = img.astype( numpy.float16 )
    img = ( img - numpy.float16( ARGS.mean ) ) * ARGS.scale

    return img

# ---- Step 4: Read & print inference results from the NCS -------------------

def infer_image( ser, graph, img ):

    # The first inference takes an additional ~20ms due to memory 
    # initializations, so we make a 'dummy forward pass'.
    graph.LoadTensor( img, 'user object' )
    output, userobj = graph.GetResult()

    # Load the image as a half-precision floating point array
    graph.LoadTensor( img, 'user object' )

    # Get the results from NCS
    output, userobj = graph.GetResult()

    # Sort the indices of top predictions
    order = output.argsort()[::-1][:NUM_PREDICTIONS]

    # Get execution time
    inference_time = graph.GetGraphOption( mvnc.GraphOption.TIME_TAKEN )

    # Print the results
    print( "\n==============================================================" )
    #print( "Top predictions for", ntpath.basename( imageFile ) )
    print( "Execution time: " + str( numpy.sum( inference_time ) ) + "ms" )
    print( "--------------------------------------------------------------" )
    for i in range( 0, NUM_PREDICTIONS ):
        print( "%3.1f%%\t" % (100.0 * output[ order[i] ] )
               + labels[ order[i] ] )
    print( "==============================================================" )

    try:
        if output[ order[0] ] > 0.96:
            if labels[ order[0] ] == "Naruto: Bird Hand Seal":
                print("Bird was here")
                ser.write(bytes([1]))   #unlock
            elif labels[ order[0] ] == "Naruto: Boar Hand Seal":
                print("Boar was here")
                ser.write(bytes([2]))   #lock
    except serial.SerialException as e:
        print(e)
        process = subprocess.call('sudo rfcomm connect hci0 98:D3:31:FC:7F:99 1 &', shell=True)
        ser = serial.Serial(port='/dev/rfcomm0', baudrate=9600)
        
            
    # If a display is available, show the image on which inference was performed
    #if 'DISPLAY' in os.environ:
        #skimage.io.imshow( imageFile )
        #skimage.io.show()

# ---- Step 5: Unload the graph and close the device -------------------------

def close_ncs_device( device, graph ):
    graph.DeallocateGraph()
    device.CloseDevice()

# ---- Main function (entry point for this script ) --------------------------

def main(ser):

    device = open_ncs_device()
    graph = load_graph( device )

    try:
        while True:
            with picamera.PiCamera() as camera:
                camera.capture(imageFile)
            #img_draw = skimage.io.imread( ARGS.image )
            img_draw = skimage.io.imread( imageFile )
            img = pre_process_image( img_draw )
            infer_image( ser, graph, img )
    except KeyboardInterrupt:
        print("exiting..")
    except:
        import traceback
        traceback.print_exc()
    finally:
        ser.close()
        
    close_ncs_device( device, graph )

# ---- Define 'main' function as the entry point for this script -------------

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(
                         description="Image classifier using \
                         Intel® Movidius™ Neural Compute Stick." )

    parser.add_argument( '-g', '--graph', type=str,
                         default='russgraph',
                         help="Absolute path to the neural network graph file." )

    #parser.add_argument( '-i', '--image', type=str,
    #                     default='../../data/images/cat.jpg',
    #                     help="Absolute path to the image that needs to be inferred." )
    

        #parser.add_argument( '-i', '--image', type=str,
                             #default='/home/pi/workspace/ncappzoo/apps/image-classifier/newimage.jpg',
                             #help="Absolute path to the image that needs to be inferred." )
    

    parser.add_argument( '-l', '--labels', type=str,
                         default='../../data/ilsvrc12/synset_words.txt',
                         help="Absolute path to labels file." )

    parser.add_argument( '-M', '--mean', type=float,
                         nargs='+',
                         default=[104.00698793, 116.66876762, 122.67891434],
                         help="',' delimited floating point values for image mean." )

    parser.add_argument( '-S', '--scale', type=float,
                         default=1,
                         help="Absolute path to labels file." )

    parser.add_argument( '-D', '--dim', type=int,
                         nargs='+',
                         default=[227, 227],
                         help="Image dimensions. ex. -D 224 224" )

    parser.add_argument( '-c', '--colormode', type=str,
                         default="bgr",
                         help="RGB vs BGR color sequence. This is network dependent." )

    ARGS = parser.parse_args()

    # Load the labels file
    labels =[ line.rstrip('\n') for line in
              open( ARGS.labels ) if line != 'classes\n']

    main(ser)

# ==== End of file ===========================================================
