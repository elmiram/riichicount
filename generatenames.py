# coding=utf-8
NUMS = {'1': 'i',
        '2': 'ryan',
        '3': 'san',
        '4': 'su',
        '5': 'u',
        '6': 'ryu',
        '7': 'chi',
        '8': 'pa',
        '9': 'kyu',
        }

SUITS = {'s': 'sou',
         'm': 'man',
         'p': 'pin'
         }

WINDS = {'ea': u'Восток',
         'so': u'Юг',
         'we': u'Запад',
         'no': u'Север'}

DRAGONS = {'re': u'чун',
           'gr': u'хацу',
           'wh': u'хаку'}

HONORS = {'ea': 'ton',
          'so': 'nan',
          'we': 'sha',
          'no': 'pey',
          're': 'chun',
          'gr': 'hatsu',
          'wh': 'haku'}

directions = ['', 'r', 'd', 'l']

INDICATORS = {'1': '2',
              '2': '3',
              '3': '4',
              '4': '5',
              '5': '6',
              '6': '7',
              '7': '8',
              '8': '9',
              '9': '1',
              'ea': 'so',
              'so': 'we',
              'we': 'no',
              'no': 'ea',
              're': 'wh',
              'gr': 're',
              'wh': 'gr'
              }

if __name__ == "__main__":
    for z in directions:
        for i in SUITS:
            for y in NUMS:
                if z == '':
                    # {{url_for('static', filename='img/%d%s%s.gif')}}
                    print(".%s%s%s{content:url({{url_for('static', filename='img/%s%s%s.gif')}}) }" % (
                    NUMS[y], SUITS[i], z, y, i, z))
                else:
                    print(".%s%s_%s{content:url({{url_for('static', filename='img/%s%s%s.gif')}}) }" % (
                    NUMS[y], SUITS[i], z, y, i, z))
        for h in HONORS:
            if z == '':
                print(".%s%s{content:url({{url_for('static', filename='img/%s%s.gif')}}) }" % (HONORS[h], z, h, z))
            else:
                print(".%s_%s{content:url({{url_for('static', filename='img/%s%s.gif')}}) }" % (HONORS[h], z, h, z))
