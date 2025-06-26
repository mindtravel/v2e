import numpy as np
import logging

import torch, os
from engineering_notation import EngNumber  # only from pip
import atexit
import struct

# check https://gitlab.com/inivation/dv/dv-processing to install dv-processing-python
import dv_processing as dv

from v2ecore.v2e_utils import v2e_quit

logger = logging.getLogger(__name__)

TIMESTAMP_COLUMN = 0
X_COLUMN = 1
Y_COLUMN = 2
POLARITY_COLUMN = 3

class NpzOutput:
    """
    outputs npz format DVS data from v2e
    """


    def __init__(self, folder_path: str, output_width=640, output_height=480):
        self.folder_path = folder_path
        self.events = np.zeros(shape = (0, 4))  # empty array to store events
        # self.numEventsWritten = 0
        # self.numOnEvents=0
        # self.numOffEvents=0
        # logging.info('opening AEDAT-4.0 output file {} in binary mode'.format(folder_path))

        # self.flipy = False 
        # self.flipx = False 
        # self.sizex = output_width
        # self.sizey = output_height
         
        # self.store = dv.EventStore()

        # resolution = (640, 480)
        # # Event only configuration
        # config = dv.io.MonoCameraWriter.EventOnlyConfig("DVXplorer_sample", resolution)

        # # Create the writer instance, it will only have a single event output stream.
        # self.writer = dv.io.MonoCameraWriter(folder_path, config)

    def cleanup(self):
        self.close()

    def close(self):
        if self.writer:
            logger.info("Closing {} after writing {} events ({} on, {} off)".
                        format(self.folder_path,
                               EngNumber(self.numEventsWritten),
                               EngNumber(self.numOnEvents),
                               EngNumber(self.numOffEvents),
                               ))
            
            self.writer.writeEvents(self.store)
            self.writer = None

    def savezEvents(self, frame_idx):
        """Save events to ".npy" file.

        In the "events" array columns correspond to: x, y, timestamp, polarity.

        We store:
        (1) x,y coordinates with uint16 precision.
        (2) timestamp with float32 precision.
        (3) polarity with binary precision, by converting it to {0,1} representation.

        """
        if (0 > self.events[:, X_COLUMN]).any() or (self.events[:, X_COLUMN] > 2 ** 16 - 1).any():
            raise ValueError("Coordinates should be in [0; 2**16-1].")
        if (0 > self.events[:, Y_COLUMN]).any() or (self.events[:, Y_COLUMN] > 2 ** 16 - 1).any():
            raise ValueError("Coordinates should be in [0; 2**16-1].")
        if ((self.events[:, POLARITY_COLUMN] != -1) & (self.events[:, POLARITY_COLUMN] != 1)).any():
            raise ValueError("Polarity should be in {-1,1}.")
        # self.events = np.copy(self.events)
        x, y, timestamp, polarity = np.hsplit(self.events, self.events.shape[1])
        polarity = (polarity + 1) / 2
        # print(os.path.join(self.folder_path, "{:06d}.npz".format(frame_idx)))
        np.savez(
            os.path.join(self.folder_path, "{:06d}.npz".format(frame_idx)),
            x=x.astype(np.uint16),
            y=y.astype(np.uint16),
            t=timestamp.astype(np.float32),# key从timestamp变成了t
            p=polarity.astype(np.bool),
        )
        self.events = np.zeros(shape = (0, 4)) # reset events after saving
            # logger.info('wrote {} events'.format(n))
             
    def appendEvents(self, events: np.ndarray):
        # print('appendEvents called with shape:', self.events.shape)
        if self.events.shape[0] == 0:
            self.events = events
        else:
            np.concatenate((self.events, events), axis=0)
        
# haven't modified yet, don't use it
if __name__ == '__main__':
    class NpzOutputTt():
        f = NpzOutput('aedattest.aedat4')
        e = [[1, 400, 0, 0], [2, 0, 400, 0], [3, 300, 400, 0], [4, 400, 300, 1], [5, 400, 300, 0]]
        ne = np.array(e)
        eventsNum = 2000 * 5
        nne = np.tile(ne, (int(eventsNum/5), 1))
        nne[:, 0] = np.arange(1, eventsNum + 1)
        f.appendEvents(nne)
        print('wrote {} events'.format(nne.shape[0]))
        f.close()




