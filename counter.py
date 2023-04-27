import datetime
class Counter:
    def __init__(self,cross,out_file='totals.csv'):
        self.cross = cross # point0, point2
        self.out_file = out_file
        self.reset()
    def check_crosses(self,objs):
        for obj in objs:
            if not obj.get_has_crossed():
                has_crossed = self.check_cross(obj)
                if has_crossed:
                    obj.mark_crossed()
                    direction= obj.get_direction()
                    self.totals[direction]+=1
    def reset(self):
        self.totals = {'up':0,'down':0}
    def check_cross(self,obj):
        x0_0, y0_0 = self.cross[0]
        x1_0, y1_0 = self.cross[1]
        x0_1, y0_1 = obj.start_centroid
        x1_1, y1_1 = obj.current_centroid
        dx0 = x1_0 - x0_0
        dy0 = y1_0 - y0_0
        dx1 = x1_1 - x0_1
        dy1 = y1_1 - y0_1
        denominator = dx1 * dy0 - dy1 * dx0
        if denominator == 0:
            return False  # lines are parallel
        t = ((x0_0 - x0_1) * dy1 - (y0_0 - y0_1) * dx1) / denominator
        u = ((x0_0 - x0_1) * dy0 - (y0_0 - y0_1) * dx0) / denominator
        if 0 <= t <= 1 and 0 <= u <= 1:
            return True  # segments intersect
        else:
            return False  # segments do not intersect
    def get_results(self):
        return self.totals
    def print_results(self):
        new_line = f'{self.get_current_datetime()},{self.totals["up"]},{self.totals["down"]}\n'
        with open(self.out_file,'a') as f:
            f.write(new_line)
    def get_current_datetime(self):
        now = datetime.datetime.now()
        return now.strftime('%m/%d/%Y %H:%M:%S')
