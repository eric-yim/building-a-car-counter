class TrackedObject:
    def __init__(self,idx,box):
        self.idx = idx
        self.box = box
        self.unused_count = 0
        self.start_centroid = [(box[0]+box[2])/2,(box[1]+box[3])/2]#x,y
        self.current_centroid = [(box[0]+box[2])/2,(box[1]+box[3])/2]
        self.has_crossed = False

    def update(self,box):
        self.box = box
        self.unused_count = 0
        self.current_centroid = [(box[0]+box[2])/2,(box[1]+box[3])/2]#x,y
        if self.has_crossed:
            self.cross_count+=1
            if self.cross_count>=self.reset_threshold:
                self.has_crossed=False
                self.start_centroid = [(box[0]+box[2])/2,(box[1]+box[3])/2]#x,y
    def unused(self):
        self.unused_count+=1
    def get_has_crossed(self):
        return self.has_crossed
    def mark_crossed(self):
        self.has_crossed = True
        self.cross_count = 0
        self.reset_threshold = 6
        self.up_or_down()
    def up_or_down(self):
        y0 = self.start_centroid[1]
        y1 = self.current_centroid[1]
        self.direction='up'
        if y1>y0:
            self.direction = 'down'
    def get_direction(self):
        return self.direction

class Tracker:
    def __init__(self):
        self.objects = []
        self.count = 0
        self.unused_threshold = 10
        self.print = False
    def track(self,pred_boxes):
        # if len(self.objects)==0:
        #     for box in pred_boxes:
        #         self.objects.append(TrackedObject(self.count,box))
        #         self.count+=1
        #     return
        self.match(pred_boxes)

    def match(self,new_boxes):
        old_boxes = [obj.box for obj in self.objects]
        #old_unmatched = []
        remove_oboxes = [False for _ in old_boxes]
        used_boxes = [False for _ in new_boxes]
        matched = []
        for o,obox in enumerate(old_boxes):
            #greedy
            ious = [self.iou(obox,nbox,ubox) for nbox,ubox in zip(new_boxes,used_boxes)]
            #print(ious)
            idx = self.max_idx(ious)
            
            if idx is None:
                #old_unmatched.append(self.objects[o])
                self.objects[o].unused()
                #print(ious,idx,self.objects[o].unused_count)
                 # remove lingering boxes
                if self.objects[o].unused_count >= self.unused_threshold:
                    remove_oboxes[o]=True
            else:
                used_boxes[idx]=True
                self.objects[o].update(new_boxes[idx])

        # remove lingering boxes
        self.objects = [obj for obj,rbox in zip(self.objects,remove_oboxes) if not rbox]

        temp = len(self.objects)
        # unmatched new boxes
        for nbox,ubox in zip(new_boxes,used_boxes):
            if not ubox:
                self.objects.append(TrackedObject(self.count,nbox))
                self.count+=1
        if self.print:
            self.print_info()
    def print_info(self):
        info = {
            "OldBoxes": len(remove_oboxes),
            "RemovedBoxes": sum(remove_oboxes),
            "Matches": sum(used_boxes),
            "NewBoxes": len(new_boxes),
            "NewBoxesAppended":len(self.objects)-temp,
            "Total": len(self.objects)
        }
        for k,v in info.items():
            print(f"{k}:{v}")
        print('='*40)

       

        



        
    def iou(self,obox,nbox,ubox):
        if ubox:
            return 0
        #print(obox,nbox)
        #print(nbox)
        x1_1, y1_1, x1_2, y1_2 = obox
        x2_1, y2_1, x2_2, y2_2 = nbox
        intersection_width = max(min(x1_2, x2_2) - max(x1_1, x2_1),0)
        intersection_height = max(min(y1_2, y2_2) - max(y1_1, y2_1),0)
        intersection_area = intersection_width * intersection_height
        box1_area = (x1_2 - x1_1) * (y1_2 - y1_1)
        box2_area = (x2_2 - x2_1) * (y2_2 - y2_1)
        union_area = box1_area + box2_area - intersection_area
        return intersection_area / union_area
    def max_idx(self,my_list):
        # only positive numbers for my_list
        best = 1e-5
        best_idx = None
        for idx,item in enumerate(my_list):
            if item > best:
                best=item
                best_idx = idx
        return best_idx
