import mtutil
import motadata

import json
import sys
import os

def check(route):
    mota = mtutil.MotaMain(motadata)
    state = mota.eval_route(route, verbose=os.getenv('VERBOSE'))
    stat = state[0]
    print('Final stat', stat)
    assert route[-1] == 1, 'game did not terminate'
    assert not stat['salt'] and not stat['big_salt'], 'you have resource debt'
    assert stat['hp'] > 0
    print('SCORE', stat['hp'])
    return stat['hp']

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        route = json.load(f)
    value = -1
    try:
        value = check(route)
    except Exception as e:
        print('Your solution does not work because:', e)
    if value > 0:
        print('Congratulations!\n'
            'You solved this challenge "'+motadata.game_name+'".\n'
            'Go to "'+motadata.game_link+'" and submit your score by:\n'
            'Battling the enemies in these coordinates in order and collect resources:')
        for i in route:
            x, y, z = motadata.major_coords[i]
            print(motadata.floor_ids[z], ':', 'x =', x, 'y =', y)
