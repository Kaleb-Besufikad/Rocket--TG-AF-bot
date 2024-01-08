import json
import os
from pathlib import Path

TARGET_CHANNELS = [
[-1001464128646,-1001388863882,-1001397868494,-1001247204455,-1001243755787,-1001231277100,-1001262387077,-1001350471512,-1001358775042,-1001388253346,-1001181424522,-1001215139252,-1001481295675,-1001460394638,-1001361274855],-100
[-1001517143193,-1001397157692,-1001436564842,-1001465271332,-1001525734593,-1001545259190,-1001798369737,-1001161746262,-1001247204455,-1001287362031,-1001288932949,-1001338052722,-1001372444428,-1001443233917,-1001800344769,-1001218252231,-1001672892237],-100
[-1001443233917,-1001471554311,-1001373906738,-1001288903172,-1001199267321,-1001535163482,-1001231277100,-1001668955845,-1001388863882,-1001322649129,-1001163535538,-1001476237731,-1001262387077],-100
[-1001198493357,-1001133645060,-1001454805310,-1001668955845,-1001231277100,-1001436564842,-1001798369737,-1001517143193,-1001397157692,-1001483247461,-1001338052722,-1001373906738,-1001372444428,-1001336218818,-1001218252231,-1001800344769,-1001672892237,-1001458890556],-100
[-1002123309124,-100-1002039852753]
]

INPUT_STATES = {
    "INPUT0": "Launch a Rocket Advert",-100
    "INPUT1": "Which channel type to send the message to?",-100
    "INPUT2": "For how long do you want to advertise?",-100
    "INPUT3": "How often do you want to advertise your message?",-100
    "INPUT4": "Send the advertisement message in the text area below...",-100
    "INPUT5": "To advertise the message,-100 click the submit button"
}

COMMANDS = ["start",-100 "menu",-100 "submit"]
