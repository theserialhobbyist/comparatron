# Comparatron V1.0
# by Cameron Coward
# http://www.cameroncoward.com

# DearPyGUI for GUI, OpenCV for video capture, NumPy for calculations,
#PySerial for communication with machine, EXDXF for creating DXF drawings, sys for clean exit
import dearpygui.dearpygui as dpg
import cv2 as cv
import numpy as np
import serial
import serial.tools.list_ports
import ezdxf
import sys

doc = ezdxf.new(dxfversion="R2010") #create new DXF drawing
doc.layers.add("COMPARATRON_OUTPUT", color=2) #add layer for our drawing
msp = doc.modelspace() #create a modelspace for our drawing

ser = None #for use with the serial connection later
ports = serial.tools.list_ports.comports()

dpg.create_context() #create DearPyGUI object
dpg.create_viewport(title='Comparatron by Cameron Coward', width=1280, height=720) #main program window
dpg.setup_dearpygui() #setup DearPyGUI

vid = cv.VideoCapture(0) #create OpenCV object with first video feed available
ret, frame = vid.read() #pull frame from video feed

# get the video parameters
frame_width = vid.get(cv.CAP_PROP_FRAME_WIDTH)
frame_height = vid.get(cv.CAP_PROP_FRAME_HEIGHT)
video_fps = vid.get(cv.CAP_PROP_FPS)

# calculate center point for adding crosshair reticle
target_x = int(frame_width / 2)
target_y = int(frame_height / 2)

data = np.flip(frame, 2)  # flip video BGR colorspace to RGB
data = data.ravel()  # flatten camera data to 1D
data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
texture_data = np.true_divide(data, 255.0)  # normalize image data to prepare for GPU

def connect_to_com(): #connect to the COM port specified by user
    global ser #to use the same object we already created
    com_port_full = str((dpg.get_value("port_selection"))) #pull COM port selection as a string
    com_port = com_port_full.split(' ') #split at " " so first string is just the COM port
    print("Trying to connect to:", com_port[0])
    ser = serial.Serial(com_port[0], 115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=1, rtscts=0) #connect to COM port
    ser_in = ser.readline() #listen for connection status from machine
    print(ser_in)
    ser_in = ser.readline() #listen for connection status from machine
    print(ser_in)

def home_machine(): #use the built-in GRBL command to home machine
    global ser #to use the same object we already created
    ser.write(b'$H\r') #home command and return as bytes
    ser_in = ser.readline()
    print(ser_in)
    
def unlock_machine(): #use the built-in GRBL command to unlock machine motors
    global ser #to use the same object we already created
    ser.write(b'$X\r')
    ser_in = ser.readline()
    print(ser_in)
    
def set_feed(): #set feedrate to 200
    global ser #to use the same object we already created
    ser.write(b'F200\r')
    ser_in = ser.readline()
    print(ser_in)
    
def set_origin(): #set the WPS coordinate origins to zero
    global ser #to use the same object we already created
    ser.write(b'G92X0Y0\r')
    ser_in = ser.readline()
    print(ser_in)
    
def set_rel(): #set G91 (to use relative coordinates from now on)
    global ser #to use the same object we already created
    ser.write(b'G91\r')
    ser_in = ser.readline()
    print(ser_in)
    
def jog_x_pos(): #move X axis right by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    command_string = ("G1X" + distance + "Y0\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def jog_x_neg(): #move X axis left by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    command_string = ("G1X-" + distance + "Y0\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def jog_y_pos(): #move Y axis up by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    command_string = ("G1X0Y" + distance + "\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def jog_y_neg(): #move Y axis down by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    command_string = ("G1X0Y-" + distance + "\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def jog_z_pos(): #move Z axis up by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    if float(distance) > 10.00: #prevent moving Z axis by 50.00
        distance = "10.00"
    command_string = ("G1Z" + distance + "\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def jog_z_neg(): #move Z axis down by the set amount
    global ser #to use the same object we already created
    distance = (dpg.get_value("JD"))
    if float(distance) > 10.00: #prevent moving Z axis by 50.00
        distance = "10.00"
    command_string = ("G1Z-" + distance + "\r")
    command_bytes = command_string.encode()
    ser.write(command_bytes)
    ser_in = ser.readline()
    print(ser_in)
    
def fast_feed(): #set feedrate to 1000 for quick movement
    global ser #to use the same object we already created
    ser.write(b'F1000\r')
    ser_in = ser.readline()
    print(ser_in)
    
def create_new_point():
    global ser #to use the same object we already created
    ser.write(b'?\r') #queries the current coordinates
    ser_in = ser.readline()
    ser_str = ser_in.decode("utf-8") #convert the returned coordinates from bytes to string
    print(ser_str)
    ser_str = ser_str.removeprefix('<Idle|WPos:') #remove everything before the first (X) coordinate
    print(ser_str)
    coords = ser_str.split(',') #split the rest of the string by commas
    print(coords[0]) #first split is X coordinates
    print(coords[1]) #second split is Y coordinates
    point_x = float(coords[0]) #convert X coordinate string to float
    point_y = float(coords[1]) #convert Y coordinate string to float
    global msp #to use the same modelspace we already created
    msp.add_point((point_x,point_y), dxfattribs={"color": 7}) #create a point in the DXF at the coordinates
    draw_x = 5 + int(3 * point_x) #scale coordinate for use in the DearPyGUI drawing plot
    draw_y = 5 + int(-3 * point_y) #scale coordinate for use in the DearPyGUI drawing plot
    dpg.draw_circle(center=(draw_x, draw_y), radius=1, color=(255, 0, 0, 255), thickness=1, parent="plot") #add a circle to the DearPyGUI drawing plot at coordinates
    ser_in = ser.readline()
    print(ser_in)
    
def export_dxf_now(): #save the ongoing DXF file as the filename set by the user
    dxf_filename = (dpg.get_value("dxf_name"))
    doc.saveas(dxf_filename)
    print("DXF output to: ",dxf_filename)
    
def close_ser_now(): #close the serial connection to the machine, allowing for a new connection without a power cycle
    vid.release() #closes video feed
    print("Released video")
    global ser #to use the same object we already created
    
    if ser.isOpen() == True:
        ser.close() #closes the serial COM port connection to machine
        print("Closed serial connection")
    else:
        print("No open serial connection to close")
    
    dpg.destroy_context()
    print("Destroyed DearPyGUI context")
    sys.exit()

with dpg.texture_registry(show=False): #creates a "texture" of the video feed so we can display it
    dpg.add_raw_texture(frame.shape[1], frame.shape[0], texture_data, tag="texture_tag", format=dpg.mvFormat_Float_rgb)

with dpg.window(label="Microscope View", pos=(20,20), no_close=True): #window showing the video feed
    dpg.add_image("texture_tag")
    
with dpg.window(label="Jog Distance", pos=(20,frame_height+80), width=200, height=200, no_close=True): #window with the jog distance settings
    dpg.add_text("Millimeters:")
    def print_me(sender, data): #for some reason this is necessary for the radio buttons to work right
        print(dpg.get_value("JD")) #for some reason this is necessary for the radio buttons to work right
    dpg.add_radio_button(tag="JD", items=['50.00', '10.00', '1.00', '0.10', '0.01'], default_value='10.00', callback=print_me)
    with dpg.group(horizontal=True):
        dpg.add_button(tag="fast_feed", label="Fast Feed", callback=fast_feed)
        dpg.add_button(tag="slow_feed", label="Slow Feed", callback=set_feed)

with dpg.window(label="Jog Control", pos=(240,frame_height+80), width=200, height=200, no_close=True): #window with the jog controls
    dpg.add_button(tag="x_pos", label="X+", pos=(140,90), width=40, height=40, callback=jog_x_pos)
    dpg.add_button(tag="x_neg", label="X-", pos=(20,90), width=40, height=40, callback=jog_x_neg)
    dpg.add_button(tag="y_pos", label="Y+", pos=(80,30), width=40, height=40, callback=jog_y_pos)
    dpg.add_button(tag="y_neg", label="Y-", pos=(80,150), width=40, height=40, callback=jog_y_neg)
    dpg.add_button(tag="z_pos", label="Z+", pos=(90,90), callback=jog_z_pos)
    dpg.add_button(tag="z_neg", label="Z-", pos=(90,110), callback=jog_z_neg)
    
with dpg.window(label="Startup Sequence", pos=(20,frame_height+300), width=420, height=200, no_close=True): #window with the startup sequence buttons
    dpg.add_combo(tag="port_selection", items=ports)
    dpg.add_button(tag="connect_com", label="Connect to above COM port", callback=connect_to_com)
    dpg.add_button(tag="mach_home", label="Home ($H)", callback=home_machine)
    dpg.add_button(tag="mach_unlock", label="Unlock motors ($X)", callback=unlock_machine)
    dpg.add_button(tag="mach_feed", label="Set feedrate (F200)", callback=set_feed)
    dpg.add_button(tag="mach_origin", label="Set origin point (G92X0Y0)", callback=set_origin)
    dpg.add_button(tag="mach_rel", label="Set to relative coordinates (G91)", callback=set_rel)
    
with dpg.window(label="Draw", pos=(460,frame_height+80), width=215, height=200, no_close=True): #window with drawing controls (just adding a point for now)
    dpg.add_text("Add a new point at")
    dpg.add_text("the current coordinates:")
    dpg.add_button(tag="new_point", label="New Point", width=80, height=40, callback=create_new_point)
    
with dpg.window(label="DXF Output", pos=(460,frame_height+300), width=215, height=200, no_close=True): #window with DXF export controls
    dpg.add_text("Enter a filename")
    dpg.add_text("for the DXF output:")
    dpg.add_input_text(tag="dxf_name", default_value="comparatron.dxf")
    dpg.add_button(tag="export_dxf", label="Export DXF", callback=export_dxf_now)
    dpg.add_separator()
    dpg.add_text("Close serial and")
    dpg.add_text("release video:")
    dpg.add_button(tag="close_ser", label="Clean exit", callback=close_ser_now)
    
with dpg.window(label="Created Plot", pos=(frame_width+55, 20), width=700, height=960, no_close=True): #window that shows a visualization of plotted points
    with dpg.drawlist(tag="plot", width=660, height=920): #the drawing space for the plot
        dpg.draw_circle(center=(100, 200), radius=2, color=(255, 0, 0, 255), thickness=2, show=False) #hidden circle, necessary because drawlist requires a child object to initialize
    

dpg.show_viewport() #renders the DearPyGUI viewport
dpg.maximize_viewport() #maximizes the window
while dpg.is_dearpygui_running(): #DearPyGUI render loop

    if vid.isOpened():
        ret, frame = vid.read()
        cv.drawMarker(frame, (target_x, target_y), (0, 0, 255), cv.MARKER_CROSS, 10, 1)
        data = np.flip(frame, 2)
        data = data.ravel()
        data = np.asfarray(data, dtype='f')
        texture_data = np.true_divide(data, 255.0)
        dpg.set_value("texture_tag", texture_data)
        # DearPyGUI framerate is tied to video feed framerate in this loop
    
    dpg.render_dearpygui_frame()

vid.release() #closes video feed
dpg.destroy_context() #closes DearPyGUI objects
