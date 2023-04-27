import datetime
import matplotlib.pyplot as plt
FILENAME = 'totals.csv'
FIRST_TIME = '04/07/2023 05:00:00'
def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
class LineItem:
    def __init__(self,dt,up,down):
        self.dt = dt
        self.up = up
        self.down = down
        self.total = up+down
class Reader:
    def __init__(self,fname):
        with open(fname,'r') as f:
            self.lines = f.read().splitlines()
    def parse(self):
        return [self.parse_line(line) for line in self.lines]

    def parse_line(self,line):
        words = line.split(',')
        dt = parse_date(words[0])
        up,down = int(words[1]),int(words[2])
        return LineItem(dt,up,down)
class Grouper:
    def __init__(self,first_time,increment=datetime.timedelta(minutes=10)):
        self.first_time=parse_date(first_time)
        self.increment = increment
        self.results = []
        
    def read_items(self,items):
        current_time = self.first_time
        current_group = [current_time,0,0] # up,down
        for item in items:
            if item.dt >= current_time + self.increment:
                self.results.append(current_group)
                current_time = current_time + self.increment
                current_group = [current_time,0,0] # up,down
            if item.dt < current_time:
                continue
            current_group[1]+=item.up 
            current_group[2]+=item.down
        self.results.append(current_group)


def plot(grouper):
    datetimes = [i[0].strftime('%H:%M') for i in grouper.results][::-1]
    count_up = [i[1] for i in grouper.results][::-1]
    count_down = [i[2] for i in grouper.results][::-1]
    total_count = [sum(x) for x in zip(count_up, count_down)]

    plt.barh(datetimes, count_up, label='Cars to Freeway')
    plt.barh(datetimes, total_count, label='Total Cars', left=count_up)

    plt.xlabel('Cars')
    plt.ylabel('Times')
    plt.legend()
    plt.show()
def main():
    reader = Reader(FILENAME)
    line_items = reader.parse()

    grouper = Grouper(FIRST_TIME)
    grouper.read_items(line_items)

    plot(grouper)





    

if __name__=='__main__':
    main()