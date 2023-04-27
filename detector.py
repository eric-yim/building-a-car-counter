import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
#from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
NAME_OF_IMAGE = 'sample.png'
NAME_OF_WINDOW = 'WINDOW'
class Detector:
    def __init__(self):
        cfg = get_cfg()

        # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2  # set threshold for this model
        # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        self.predictor = DefaultPredictor(cfg)
        self.cfg = cfg
    def detect(self,im):
        return self.predictor(im)
    def visualize(self,im,outputs):
        # We can use `Visualizer` to draw the predictions on the image.
        v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), scale=1.2)
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        return out.get_image()[:, :, ::-1]
    def get_fields(self,outputs):
        return outputs["instances"].to("cpu").get_fields()
def filter_fields(fields):
    pred_boxes = fields['pred_boxes'].tensor.numpy()
    # mean_height = mean([height(box) for box in pred_boxes])
    # print(mean_height)
    scores = fields['scores'].numpy()
    pred_classes = fields['pred_classes'].numpy()
    #filter criteria
    valid0 = pred_classes ==2 
    valid1 = filter_by_size(pred_boxes)
    valid2 = valid0*valid1
    # create new fields
    fields = {
        'pred_boxes':pred_boxes[valid2],
        'scores':scores[valid2],
        'pred_classes':pred_classes[valid2]
    }
    return fields
def filter_by_size(pred_boxes):
    widths = pred_boxes[:,2]-pred_boxes[:,0]
    heights = pred_boxes[:,3]-pred_boxes[:,1]
    return (widths < 60.0) * (widths > 20) * (heights < 60.0) * (heights > 20)
def width(box):
    x0,_,x1,_ = box
    return x1-x0
def height(box):
    _,y0,_,y1 = box
    return y1-y0
def mean(a_list):
    return sum(a_list)/float(len(a_list))
def visualize(im,fields):
    pred_boxes = fields['pred_boxes']
    scores = fields['scores']
    pred_classes = fields['pred_classes']
    for box,pred_class in zip(pred_boxes,pred_classes):
        box = [round(int(b)) for b in box]
        cv2.rectangle(im,box[:2],box[2:],[0,255,0],2)
    return im

        
def main():
    # Create a window
    cv2.namedWindow(NAME_OF_WINDOW,cv2.WINDOW_KEEPRATIO)

    # Load the image
    im = cv2.imread(NAME_OF_IMAGE)
    
    # Use the detectron2 model
    detector = Detector()
    outputs = detector.detect(im)
    fields = detector.get_fields(outputs)
    fields = filter_fields(fields)
    im_with_results = visualize(im,fields)

    # Display image with results
    cv2.imshow(NAME_OF_WINDOW,im_with_results)
    # Displays image for 10 seconds
    cv2.waitKey(10000)


if __name__=='__main__':
    main()