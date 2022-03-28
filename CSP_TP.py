import time
import argparse

def read_file(path):
    landscape = []
    tiles = {}
    targets = []
    with open(path, "r") as f:
        data = f.readlines()
    k = 0
    for i in data:
        i = i.strip('\n')
        if k == 1:
            landscape.append(i)
        elif k == 2:
            for j in i.strip('{').strip('}').split(', '):
                a = j.split('=')
                tiles[a[0]] = int(a[1])
            k = 0
        elif k == 3:
            a = i.split(':')
            targets.append(int(a[1]))
            if len(targets) == 4:
                break
        if i == '# Landscape':
            k = 1
        elif i == '# Tiles: ':
            k = 2
        elif i == '# Targets: ':
            k = 3
    landscape = landscape[:-2]
    for i in range(len(landscape)):
        landscape[i] = list(map(int, landscape[i][0::2].replace(' ', '0')))

        while len(landscape[i]) != len(landscape):
            landscape[i].append(0)

    return landscape, tiles, targets

def transfer(landscape):
    res = []
    for col in range(0,len(landscape[0]),4):
        for row in range(0,len(landscape),4):
            count_ob = []
            count_el = []
            dic = {}
            a = landscape[row+1][col+1:col+4]
            a.extend(landscape[row+2][col+1:col+4])
            a.extend(landscape[row + 3][col + 1:col + 4])
            b = a[0:2]
            b.extend(a[3:5])
            for i in range(1,5):
                count_el.append(a.count(i))
                count_ob.append(b.count(i))
            dic['OUTER_BOUNDARY'] = count_ob
            dic['EL_SHAPE'] = count_el
            res.append(dic)

    return res

class CSP():
    def __init__(self, variables, domains):
        self.variables = variables
        self.domains = domains

    # back_tracking
    def back_tracking(self, assignment,land, tiles, targets):
        if len(assignment) == len(self.variables) and sum_tiles(assignment):
            return assignment

        unassigned = [v for v in self.variables if v not in assignment]
        #first = unassigned[0]  # natural order

        # MRV min remaining values
        first = self.MRV(unassigned)

        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value

            # AC3
            if self.AC3(local_assignment):
                result = self.back_tracking(local_assignment,land, tiles, targets)
                if result is not None:
                    return result
        return None

    def MRV(self, assignment):
        # MRV:find the variable that has the smallest domain
        size = float('inf')
        for variable in assignment:
            domain = self.domains[variable]
            if len(domain)<size:
                size = len(domain)
                mrv = variable

        return mrv

    def AC3(self, assignment):
        res = [0, 0, 0, 0]
        fb = 0
        ob = 0
        el = 0
        for key, value in assignment.items():
            if value == 'FULL_BLOCK':
                add = [0, 0, 0, 0]
                fb += 1
                if fb > tiles[value]:
                    return False
            elif value == 'OUTER_BOUNDARY':
                add = land[key][value]
                ob += 1
                if ob > tiles[value]:
                    return False
            else:
                add = land[key][value]
                el += 1
                if el > tiles[value]:
                    return False
            res = list_add(res, add)
        for i in range(len(res)):
            if res[i] > targets[i]:
                return False
        if len(assignment) == len(variables):
            return res[0] == targets[0] and res[1] == targets[1] and res[2] == targets[2] and res[3] == targets[3]
        return True

def sum_tiles(assignment):
    res = [0, 0, 0, 0]
    for key, value in assignment.items():
        if value == 'FULL_BLOCK':
            add = [0,0,0,0]
        else:
            add = land[key][value]
        res = list_add(res,add)
    return res[0]==targets[0] and res[1]==targets[1] and res[2]==targets[2] and res[3]==targets[3]

def list_add(a,b):
     c = []
     for i in range(len(a)):
        c.append(a[i]+b[i])
     return c

if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser(description="CSP_TP")
    parser.add_argument('-f', default="tilesproblem_1326658913086500.txt")
    args = parser.parse_args()

    landscape, tiles, targets = read_file(args.f)
    variables = []
    n = len(landscape)//4
    for i in range(n*n):
        variables.append(i)
    domains = {}
    for variable in variables:
        domains[variable] = ["OUTER_BOUNDARY", "EL_SHAPE", "FULL_BLOCK"]
    csp = CSP(variables, domains)
    land = transfer(landscape)
    res = csp.back_tracking({}, land, tiles, targets)
    for variable, value in res.items():
        print(str(variable) + ' 4 ' + value)
    end = time.time()
    print('running_time:',end-start)