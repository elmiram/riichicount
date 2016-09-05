# coding=utf-8
import random
from generatenames import *
from collections import defaultdict
from operator import attrgetter
from itertools import combinations


def random_pick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item


class Tile:
    def __init__(self, suit='', value='', isopen=False, state='', ordering=''):
        self.suit = suit
        self.value = value
        self.isopen = isopen
        self.state = state
        self.ordering = ordering
        self.winning = False

    def issimple(self):
        if self.value not in HONORS.keys() and self.value not in ['1', '9']:
            return True
        return False

    def __str__(self):
        if self.value not in NUMS.keys() and self.value not in HONORS.keys():
            s = '<span class ="closed" ></span>'
        elif self.isopen:
            if self.suit != 'z':
                s = '<span class ="%s%s_%s" ></span>' % (NUMS[self.value], SUITS[self.suit], self.state)
            else:
                s = '<span class ="%s_%s" ></span>' % (HONORS[self.value], self.state)
        else:
            if self.suit != 'z':
                s = '<span class ="%s%s" ></span>' % (NUMS[self.value], SUITS[self.suit])
            else:
                s = '<span class ="%s" ></span>' % (HONORS[self.value])
        if self.winning:
            s = '<span style="position: relative; top:-10px;">' + s + '</span>'
        return s


class Meld:
    def __init__(self, kind='', isopen=False, tiles=None):
        self.kind = kind
        self.isopen = isopen
        self.tiles = tiles
        self.kantyan = False
        self.tanki = False
        self.pentyan = False
        self.ryanmen = False

    def last_tile(self):
        if self.kind == 'pair':
            m = random.choice([0, 1])
            self.tanki = True
        else:
            m = random.choice([0, 1, 2])
            if self.kind == 'chi':
                if m == 1:
                    self.kantyan = True
                elif (m == 0 and not self.tiles[2].issimple()) or (m == 2 and not self.tiles[0].issimple()):
                    self.pentyan = True
                else:
                    self.ryanmen = True
        return self.tiles[m]


class Hand:
    def __init__(self):
        self.tiles = defaultdict(int)
        self.round = random_pick(['ea', 'so', 'we'], [0.4, 0.4, 0.2])
        self.round_name = WINDS[self.round]
        self.seat = random.choice(list(WINDS.keys()))
        self.seat_name = WINDS[self.seat]
        self.victory = random.choice([u'рон', u'цумо'])
        self.yaku = defaultdict(int)
        self.minipoints = defaultdict(int)
        self.han = 0
        self.fu = 0
        self.points = 0
        self.dora = self.getdora()
        self.kandora = []
        self.h = []
        self.melds = []
        self.last_meld = Meld()
        self.starthand = random_pick([self.create_structure, self.create_chitoi, self.create_kokushi], [0.8, 0.15, 0.05])
        self.starthand()
        if self.victory == u'рон':
            self.last_meld.isopen = True
        self.view = self.publish(self.sorthand(self.h))
        self.isclosed = True
        self.isvalid = True
        if any(t.isopen for t in self.h):
            self.isclosed = False
        self.riichi = False
        self.isyakuman = False
        self.ippatsu = False
        self.ura = []
        self.count()

    def create_structure(self):
        a = []
        for _ in range(4):
            a.append(random_pick([self.chi, self.pon, self.kan], [0.4, 0.4, 0.2]))
        for f in a:
            self.h += f()
        self.h += self.pair()
        self.last_meld = random.choice([m for m in self.melds if not m.isopen and not m.kind == 'kan'])
        last_tile = self.last_meld.last_tile()
        last_tile.winning = True

    def create_chitoi(self):
        for _ in range(7):
            p = self.pair()
            if p[0] not in self.h:
                self.h += p
        self.last_meld = random.choice([m for m in self.melds if not m.isopen and not m.kind == 'kan'])
        last_tile = self.last_meld.last_tile()
        last_tile.winning = True

    def create_kokushi(self):
        self.h = []
        for s in SUITS:
            self.h.append(Tile(value='1', suit=s))
            self.h.append(Tile(value='9', suit=s))
        for t in HONORS:
            self.h.append(Tile(value=t, suit='z'))
        v = random.choice([1, 13])
        if v == 13:
            self.points = 64000
            self.last_meld = Meld(tiles=[random.choice(self.h)])
            last_tile = self.last_meld.tiles[0]
            last_tile.winning = True
            self.h.append(last_tile)
        else:
            win, pair = random.sample(self.h, 2)
            self.points = 32000
            self.last_meld = Meld(tiles=[win])
            last_tile = self.last_meld.tiles[0]
            last_tile.winning = True
            self.h += [pair]

    def checktiles(self, t):
        t = [(i.value, i.suit) for i in t]
        a = {}
        for el in t:
            if el in a:
                a[el] += 1
            else:
                a[el] = self.tiles[el] + 1
            if a[el] >= 4:
                return False
        for el in a:
            self.tiles[el] = a[el]
        return True

    def chi(self):
        value = random.choice(['1', '2', '3', '4', '5', '6', '7'])
        suit = random.choice(list(SUITS.keys()))
        isopen = random_pick([True, False], [0.4, 0.6])
        res = [Tile(value=value, suit=suit, isopen=isopen),
               Tile(value=str(int(value) + 1), suit=suit, isopen=isopen),
               Tile(value=str(int(value) + 2), suit=suit, isopen=isopen)]
        if isopen:
            for i in res:
                i.state = 'd'
            res[0].state = 'r'
        if not self.checktiles(res):
            return self.chi()
        self.melds.append(Meld(kind='chi', isopen=isopen, tiles=res))
        return res

    def pon(self):
        value = random.choice(list(NUMS.keys()) + list(HONORS.keys()))
        isopen = random_pick([True, False], [0.35, 0.65])
        res = [Tile(value=value, suit='z', isopen=isopen),
               Tile(value=value, suit='z', isopen=isopen),
               Tile(value=value, suit='z', isopen=isopen)]
        if value in NUMS.keys():
            suit = random.choice(list(SUITS.keys()))
            for el in res:
                el.suit = suit
        if isopen:
            for el in res:
                el.state = 'd'
            player = random.choice([0, 1, 2])
            variants = ['l', 'l', 'r']
            res[player].state = variants[player]
        if not self.checktiles(res):
            return self.pon()
        self.melds.append(Meld(kind='pon', isopen=isopen, tiles=res))
        return res

    def kan(self):
        value = random.choice(list(NUMS.keys()) + list(HONORS.keys()))
        isopen = random_pick([True, False], [0.4, 0.6])
        if value in NUMS.keys():
            suit = random.choice(list(SUITS.keys()))
            if not isopen:
                res = [Tile(value=value, suit=suit, isopen=not isopen, ordering='1'+value),
                       Tile(value=value, suit=suit, isopen=not isopen, state='d', ordering='2'+value),
                       Tile(value=value, suit=suit, isopen=not isopen, state='d', ordering='3'+value),
                       Tile(value=value, suit=suit, isopen=not isopen, ordering='4'+value)]
            else:
                res = [Tile(value=value, suit=suit, isopen=isopen, state='d'),
                       Tile(value=value, suit=suit, isopen=isopen, state='d'),
                       Tile(value=value, suit=suit, isopen=isopen, state='d'),
                       Tile(value=value, suit=suit, isopen=isopen, state='d')]
                player = random.choice([0, 1, 3])
                variants = ['l', 'l', 'l', 'r']
                res[player].state = variants[player]
        else:
            if not isopen:
                res = [Tile(value=value, suit='z', isopen=not isopen, ordering='1'+value),
                       Tile(value=value, suit='z', isopen=not isopen, state='d', ordering='2'+value),
                       Tile(value=value, suit='z', isopen=not isopen, state='d', ordering='3'+value),
                       Tile(value=value, suit='z', isopen=not isopen, ordering='4'+value)]
            else:
                res = [Tile(value=value, suit='z', isopen=isopen, state='d'),
                       Tile(value=value, suit='z', isopen=isopen, state='d'),
                       Tile(value=value, suit='z', isopen=isopen, state='d'),
                       Tile(value=value, suit='z', isopen=isopen, state='d')]
                player = random.choice([0, 1, 3])
                variants = ['l', 'l', 'l', 'r']
                res[player].state = variants[player]
        if not self.checktiles(res):
            return self.pon()
        self.kandora.append(self.getdora())
        self.melds.append(Meld(kind='kan', isopen=isopen, tiles=res))
        return res

    def pair(self):
        value = random.choice(list(NUMS.keys()) + list(HONORS.keys()))
        if value in NUMS.keys():
            suit = random.choice(list(SUITS.keys()))
            res = [Tile(value=value, suit=suit), Tile(value=value, suit=suit)]
        else:
            res = [Tile(value=value, suit='z'), Tile(value=value, suit='z')]
        if not self.checktiles(res):
            return self.pair()
        self.melds.append(Meld(kind='pair', isopen=False, tiles=res))
        return res

    def getdora(self):
        value = random.choice(list(NUMS.keys()) + list(HONORS.keys()))
        if value in NUMS.keys():
            suit = random.choice(list(SUITS.keys()))
            res = Tile(value=value, suit=suit)
        else:
            res = Tile(value=value, suit='z')
        if not self.checktiles([res]):
            return self.getdora()
        return res

    def publish(self, hand):
        h = ''
        flag = True
        for t in hand:
            if t.isopen and flag:
                flag = False
                h += '&nbsp;&nbsp;'
            h += str(t)
        return h

    def sorthand(self, h):
        return sorted(h, key=attrgetter('isopen', 'suit', 'ordering', 'value'))

    def num_dora(self, arr):
        n = 0
        for u in arr:
            d_val = INDICATORS[u.value]
            d_suit = u.suit
            for t in self.h:
                if t.value == d_val and t.suit == d_suit:
                    n += 1
        return n

    def has_dora(self):
        dora = self.num_dora([self.dora]) + self.num_dora(self.kandora)
        if dora > 0:
            self.han += dora
            self.yaku[u'дора'] += dora

    def count(self):
        self.count_yaku()
        if self.isyakuman:
            self.count_points()
            return
        if self.han == 0:
            self.isvalid = False
        self.has_dora()
        self.count_fu()
        self.count_points()
        return

    def has_riichi(self):
        if self.isclosed:
            self.riichi = random.choice([True, False])
            if self.riichi:
                self.han += 1
                self.yaku[u'риичи'] += 1
                self.ippatsu = random.choice([True, False])
                if self.ippatsu:
                    self.han += 1
                    self.yaku[u'иппацу'] += 1
                for _ in self.kandora + [self.dora]:
                    self.ura.append(self.getdora())
                if self.ura:
                    dora = self.num_dora(self.ura)
                    if dora > 0:
                        self.han += dora
                        self.yaku[u'ура-дора'] += dora

    def tsumo(self):
        if self.isclosed and self.victory == u'цумо':
            self.han += 1
            self.yaku[u'цумо'] += 1

    def pinfu(self):
        if self.isclosed:
            p = [m for m in self.melds if m.kind == 'pair'][0].tiles[0].value
            if all(m.kind == 'chi' or m.kind == 'pair' for m in self.melds):
                if self.last_meld.ryanmen is True and p not in HONORS.keys():
                    self.han += 1
                    self.yaku[u'пинфу'] += 1
                    return True
        return False

    def tanyao(self):
        if all(t.issimple() for t in self.h):
            self.han += 1
            self.yaku[u'таняо'] += 1

    def yakuhai(self):
        n = 0
        w = 0
        p = 0
        for m in self.melds:
            if m.kind in ['pon', 'kan']:
                if m.tiles[0].value == self.seat:
                    self.yaku[WINDS[self.seat].lower()] += 1
                    self.han += 1
                    w += 1
                if m.tiles[0].value == self.round:
                    self.yaku[WINDS[self.round].lower()] += 1
                    self.han += 1
                    if self.round != self.seat:
                        w += 1
                if m.tiles[0].value in DRAGONS:
                    n += 1
                    self.yaku[DRAGONS[m.tiles[0].value]] += 1
                    self.han += 1
            if m.kind == 'pair':
                if m.tiles[0].value in WINDS:
                    p = 1
        pair_value = [m for m in self.melds if m.kind == 'pair'][0].tiles[0].value
        if n == 2 and pair_value in DRAGONS:
            self.yaku[u'сёсанген'] += 2
            self.han += 2
        if n == 3:
            self.yaku = {u'дайсанген': u'якуман'}
            self.isyakuman = True
            self.points = 32000
        if w == 3 and p == 1:
            self.yaku = {u'шосуши': u'якуман'}
            self.isyakuman = True
            self.points = 32000
        if w == 4:
            self.yaku = {u'дайсуши': u'якуман'}
            self.isyakuman = True
            self.points = 64000
        if w + n == 4 and p == 1:
            self.yaku = {u'тцуисо': u'якуман'}
            self.isyakuman = True
            self.points = 32000

    def ippeikou(self):
        if self.isclosed:
            n = 0
            chis = [m for m in self.melds if m.kind == 'chi']
            for el in combinations(chis, 2):
                chi1, chi2 = el[0], el[1]
                if [(i.value, i.suit) for i in chi1.tiles] == [(i.value, i.suit) for i in chi2.tiles]:
                    n += 1
            if n == 1:
                self.yaku[u'иппейко'] += 1
                self.han += 1
            elif n == 2:
                self.yaku[u'рянпейко'] += 3
                self.han += 3

    def ittsu(self):
        h = [(i.value, i.suit) for i in self.h]
        for s in SUITS:
            if all((i, s) in h for i in NUMS.keys()):
                self.yaku[u'иццу'] += 1
                self.han += 1
                if self.isclosed:
                    self.han += 1
                    self.yaku[u'иццу'] += 1

    def sanshoku(self):
        d = {}
        chis = [m for m in self.melds if m.kind == 'chi']
        for i in chis:
            val = ''.join(t.value for t in i.tiles)
            if val not in d:
                d[val] = [1, [i.tiles[0].suit]]
            else:
                d[val][0] += 1
                d[val][1].append(i.tiles[0].suit)
        for key in d:
            if d[key][0] >= 3 and all(i in d[key][1] for i in ['s', 'm', 'p']):
                self.yaku[u'саншоку'] += 1
                self.han += 1
                if self.isclosed:
                    self.han += 1
                    self.yaku[u'саншоку'] += 1

    def chanta(self):
        j = True
        for i in self.melds:
            vals = [t.value for t in i.tiles]
            if all(v not in vals for v in list(HONORS.keys()) + ['1', '9']):
                j = False
                break
        if j is True:
            if all(v in list(HONORS.keys()) + ['1', '9'] for v in set([t.value for t in self.h])):
                self.yaku[u'хонрото'] += 2
                self.han += 2
            else:
                self.yaku[u'чанта'] += 1
                self.han += 1
                if self.isclosed:
                    self.han += 1
                    self.yaku[u'чанта'] += 1

    def junchan(self):
        j = True
        for i in self.melds:
            vals = [t.value for t in i.tiles]
            if all(v not in vals for v in ['1', '9']):
                j = False
                break
        if j is True:
            self.yaku[u'джунчан'] += 2
            self.han += 2
            if self.isclosed:
                self.han += 1
                self.yaku[u'джунчан'] += 1

    def chinitsu(self):
        if u'рянпейко' in self.yaku:
            return False
        suits = set([i.suit for i in self.h])
        if len(suits) == 1:
            self.yaku[u'чиницу'] += 5
            self.han += 5
            if self.isclosed:
                self.han += 1
                self.yaku[u'чиницу'] += 1
            return True
        return False

    def honitsu(self):
        suits = set([i.suit for i in self.h if i.suit != 'z'])
        if len(suits) == 1:
            self.yaku[u'хоницу'] += 2
            self.han += 2
            if self.isclosed:
                self.han += 1
                self.yaku[u'хоницу'] += 1

    def chitoi(self):
        if self.starthand == self.create_chitoi:
            self.han += 2
            self.yaku[u'читойцу'] += 2
            return True
        return False

    def toitoi(self):
        if all(m.kind in [u'pon', u'kan', u'pair'] for m in self.melds) and not self.sevenpairs:
            self.han += 2
            self.yaku[u'тойтой'] += 2

    def sanankou(self):
        pons = [not m.isopen for m in self.melds if m.kind in ['pon', 'kan']]
        if sum(pons) == 3:
            self.han += 2
            self.yaku[u'сананко'] += 2
        if sum(pons) == 4:
            if self.last_meld.tanki is True:
                self.yaku = {u'суанко танки': u'якуман'}
                self.isyakuman = True
                self.points = 64000
            else:
                self.yaku = {u'суанко': u'якуман'}
                self.isyakuman = True
                self.points = 32000

    def count_yaku(self):
        k = self.kokushi()
        if k:
            return
        self.has_riichi()
        self.tsumo()
        self.pnf = self.pinfu()
        self.tanyao()
        self.yakuhai()
        self.ippeikou()
        self.ittsu()
        self.sanshoku()
        self.chanta()
        self.junchan()
        self.sevenpairs = self.chitoi()
        self.toitoi()
        self.honitsu()
        self.chin = self.chinitsu()
        self.sanankou()
        self.sanshokudoko()
        self.sankantsu()
        self.churenpoto() # todo
        self.ryuisou()
        self.sukantsu()
        self.chinroto()

    def count_fu(self):
        if self.pnf:
            if self.victory == u'рон':
                self.fu = 30
                self.minipoints[u'пинфу по рон'] = 30
            else:
                self.fu = 20
                self.minipoints[u'пинфу по цумо'] = 20
            return
        if self.sevenpairs:
            self.fu += 25
            self.minipoints[u'читойцу'] = 25
            return
        elif self.isclosed and self.victory == u'рон':
            self.fu += 30
            self.minipoints[u'рон в закрытой руке'] = 30
        else:
            self.fu += 20
            self.minipoints[u'база'] = 20

        if self.victory == u'цумо' and not self.pnf:
            self.fu += 2
            self.minipoints[u'цумо'] = 2
        if not self.sevenpairs:
            pair_value = [m for m in self.melds if m.kind=='pair'][0].tiles[0].value
        else:
            pair_value = self.last_meld.tiles[0].value
        melds = [m for m in self.melds if m.kind in ['pon', 'kan']]
        flag = False
        if pair_value in DRAGONS or pair_value == self.seat:
            self.fu += 2
            flag = True
            self.minipoints[u'пара ценных тайлов'] += 2
        if pair_value == self.round:
            self.fu += 2
            flag = True
            self.minipoints[u'пара ценных тайлов'] += 2
        if self.last_meld.tanki or self.last_meld.pentyan or self.last_meld.kantyan:
            self.fu += 2
            self.minipoints[u'неудобное ожидание'] = 2
            flag = True
        if melds:
            for i in melds:
                if i.kind == 'pon':
                    if i.isopen:
                        if all(t.issimple() for t in i.tiles):
                            self.fu += 2
                            self.minipoints[u'открытый пон простых'] += 2
                        else:
                            self.fu += 4
                            self.minipoints[u'открытый пон ценных\терминалов'] += 4
                    else:
                        if all(t.issimple() for t in i.tiles):
                            self.fu += 4
                            self.minipoints[u'закрытый пон простых'] += 4
                        else:
                            self.fu += 8
                            self.minipoints[u'закрытый пон ценных\терминалов'] += 8
                else:
                    if i.isopen:
                        if all(t.issimple() for t in i.tiles):
                            self.fu += 8
                            self.minipoints[u'открытый кан простых'] += 8
                        else:
                            self.fu += 16
                            self.minipoints[u'открытый кан ценных\терминалов'] += 16
                    else:
                        if all(t.issimple() for t in i.tiles):
                            self.fu += 16
                            self.minipoints[u'закрытый кан простых'] += 16
                        else:
                            self.fu += 32
                            self.minipoints[u'закрытый кан ценных\терминалов'] += 32
            flag = True
        if not flag:
            self.fu += 2
            self.minipoints[u'нет дополнительных фу'] = 2
        self.fu = self.fu if self.sevenpairs or self.fu % 10 == 0 else (self.fu / 10 + 1) * 10

    def sanshokudoko(self):
        d = {}
        chis = [m for m in self.melds if m.kind == 'pon']
        for i in chis:
            val = ''.join(t.value for t in i.tiles)
            if val not in d:
                d[val] = [1, [i.tiles[0].suit]]
            else:
                d[val][0] += 1
                d[val][1].append(i.tiles[0].suit)
        for key in d:
            if d[key][0] >= 3 and all(i in d[key][1] for i in ['s', 'm', 'p']):
                self.yaku[u'саншоку доко'] += 2
                self.han += 2

    def sankantsu(self):
        kans = [m for m in self.melds if m.kind=='kan']
        if len(kans) == 3:
            self.yaku[u'санканцу'] += 2
            self.han += 2

    def kokushi(self):
        if self.starthand == self.create_kokushi:
            self.isyakuman = True
            if len(set(self.h)) == 13:
                self.yaku = {u'кокуши мусо с 13-сторонним ожиданием': u'якуман'}
            else:
                self.yaku = {u'кокуши мусо': u'якуман'}
            return True
        return False

    def churenpoto(self):
        if self.chin:
            a = ''.join(sorted([i.value for i in self.h]))
            a2 = ''.join(sorted([i.value for i in self.h if not i.winning]))
            if a2 == '1112345678999':
                self.isyakuman = True
                self.points = 64000
                self.yaku = {u'чуренпото': u'якуман'}
            elif '111' in a and '999' in a and all(i in a for i in '2345678'):
                self.isyakuman = True
                self.points = 32000
                self.yaku = {u'одинарный чуренпото': u'якуман'}

    def ryuisou(self):
        if self.isvalid:
            a = [i.value + i.suit for i in self.h]
            if all(g in ['2s', '3s', '4s', 'grz', '6s', '8s'] for g in a):
                self.isyakuman = True
                self.points = 32000
                self.yaku = {u'рюисоу': u'якуман'}

    def sukantsu(self):
        pons = [m for m in self.melds if m.kind=='kan']
        if len(pons) == 4:
            self.yaku = {u'суканцу': u'якуман'}
            self.isyakuman = True
            self.points = 32000

    def chinroto(self):
        if self.isvalid:
            v = [i.value for i in self.h]
            if all(i in '19' for i in v):
                self.yaku = {u'чинрото': u'якуман'}
                self.isyakuman = True
                self.points = 32000

    def count_points(self):
        multiplier = 6 if self.seat == 'ea' else 4
        if self.isyakuman:
            self.ron_points = 16000 * multiplier / 2
            self.dealer_pays = 16000
            self.others_pay = 8000
        elif self.han >= 5 or (self.han == 4 and self.fu >= 40):
            if self.han in [4, 5]:
                self.ron_points = 4000 * multiplier / 2
                self.dealer_pays = 4000
                self.others_pay = 2000
            if self.han in [6, 7]:
                self.ron_points = 6000 * multiplier / 2
                self.dealer_pays = 6000
                self.others_pay = 3000
            if self.han in [8, 9, 10]:
                self.ron_points = 8000 * multiplier / 2
                self.dealer_pays = 8000
                self.others_pay = 4000
            if self.han > 10:
                self.ron_points = 12000 * multiplier / 2
                self.dealer_pays = 12000
                self.others_pay = 6000
        else:
            round100 = lambda x: (x / 100 + 1) * 100
            base = self.fu * (2 ** (2 + self.han))  # pay if tsumo

            result = base * multiplier
            ron = result if result % 100 == 0 else round100(result)
            self.ron_points = ron

            if base % 100 == 0:
                p1 = base
                p2 = base * 2
            else:
                p1 = round100(base)
                if base % 100 > 50:
                    p2 = p1 * 2
                else:
                    p2 = p1 * 2 - 100
            self.dealer_pays = p2
            self.others_pay = p1


if __name__ == '__main__':
    for _ in range(10):
        a = Hand()
        print(a.view)
        print('<br>')
    # a = Hand()
    # a.yaku = defaultdict(int)
    # a.h = [Tile(value='2', suit='p'),
    #        Tile(value='2', suit='p'),
    #        Tile(value='2', suit='p'),
    #        Tile(value='3', suit='p'),
    #        Tile(value='3', suit='p'),
    #        Tile(value='3', suit='p'),
    #        Tile(value='4', suit='p'),
    #        Tile(value='4', suit='p'),
    #        Tile(value='4', suit='p'),
    #        Tile(value='6', suit='m'),
    #        Tile(value='7', suit='m'),
    #        Tile(value='8', suit='m'),
    #        Tile(value='7', suit='s'),
    #        Tile(value='7', suit='s')]
    # a.count()
    # for i in a.yaku:
    #     print i, a.yaku[i]
    # print a.fu
