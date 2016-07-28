# coding=utf-8
def count_points(han, fu, seat):
    round100 = lambda x: (x / 100 + 1) * 100
    base = fu * (2 ** (2 + han))  # pay if tsumo

    multiplier = 6 if seat == 'ea' else 4
    result = base * multiplier
    ron = result if result % 100 == 0 else round100(result)
    print u'Выплата по рон ', ron

    if base % 100 == 0:
        p1 = base
        p2 = base * 2
    else:
        p1 = round100(base)
        if base % 100 > 50:
            p2 = p1 * 2
        else:
            p2 = p1 * 2 - 100
    print u'Выплата по цумо %d/%d' %(p1, p2)
    print u'Если цумо вытащил дилер %d' % (p2)


count_points(3, 25, 'ea')