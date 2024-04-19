
# import motadata

class MotaMain(object):
    def __init__(self, motadata):
        self.motadata = motadata
        self.minor_adj_major = [[] for i in range(self.get_nminor())]
        for i, j in enumerate(self.motadata.major_minor_adj):
            for k in j:
                self.minor_adj_major[k].append(i)

    def get_nmajor(self): return len(self.motadata.major_desc)
    def get_nminor(self): return len(self.motadata.minor_desc)

    def can_major(self, been_set, major):
        # 0 is in been_set
        return 1 <= major < self.get_nmajor() and major not in been_set and any(i in been_set for i in self.motadata.major_adj[major])

    def get_minor_list_after_major(self, been_set, new):
        all_minors = self.motadata.major_minor_adj[new]
        return [i for i in all_minors
                if all(j not in been_set for j in self.minor_adj_major[i])]

    def init_state(self):
        return dict(self.motadata.init_stat), set([0]), []

    def calc_damage(self, stat, idx):
        enemy = self.motadata.enemy_data[idx]
        bhp, bat, bdf, bmf = stat['hp'], stat['atk'], stat['def'], stat['mdef']
        ehp, eat, edf, en = enemy['hp'], enemy['atk'], enemy['def'], enemy['attimes']
        if bat <= edf:
            return 256*(edf - bat), 1
        per = bat-edf
        if enemy.get('solid'):
            per = 1
        n = (ehp-1) // per
        if enemy.get('speedy'):
            n += 1
        n *= en
        per_e = eat-bdf
        if enemy.get('magic'):
            per_e = eat
        per_e = max(0, per_e)
        return max(0, per_e*n-bmf), 0

    def give_minor(self, stat, minor):
        v = self.motadata.minor_desc[minor]
        for i, j in v.items():
            stat[i] = stat.get(i, 0) + j

    def stat_step_major(self, stat, major, been):
        # battle or trigger event
        ty, info = self.motadata.major_desc[major]
        if ty == 'enemy':
            damage, big_salt = self.calc_damage(stat, info)
            stat['hp'] -= damage
            stat['big_salt'] += big_salt
            stat['exp'] += self.motadata.enemy_data[info]['exp']
        elif ty == 'delta':
            for i, j in info.items():
                target = j+stat.get(i)
                if i != 'hp' and target < 0:
                    stat['big_salt'] += -target
                    stat[i] = 0
                else:
                    stat[i] = target
        else:
            raise NotImplementedError
        # salt update
        if stat['hp'] <= 0:
            stat['salt'] += -stat['hp']
        if stat['big_salt'] > 0:
            stat['salt'] += stat['big_salt'] * 65536
        if stat['salt']:
            stat['salt'] += stat['salt']//self.get_nmajor() + 1
        # give minor
        for minor in self.get_minor_list_after_major(been, major):
            self.give_minor(stat, minor)
        # level up
        while stat['lv'] < len(self.motadata.levelup_desc):
            cur_case = self.motadata.levelup_desc[stat['lv']]
            if stat['exp'] >= cur_case['need']:
                if cur_case['clear']:
                    stat['exp'] -= cur_case['need']
                stat['lv'] += 1
                self.give_minor(stat, cur_case['minor'])
            else:
                break

    def step_major(self, state, major):
        assert self.can_major(state[1], major)
        stat = dict(state[0])
        # returns
        self.stat_step_major(stat, major, state[1])
        return stat, state[1].union(set([major])), state[2]+[major]

    def eval_route(self, route, verbose=False):
        state = self.init_state()
        if verbose:
            print(state)
        for i, j in enumerate(route):
            assert j
            if verbose:
                print('-- step', i, ':', j)
            state = self.step_major(state, j)
            if verbose:
                print(state[0])
        return state
