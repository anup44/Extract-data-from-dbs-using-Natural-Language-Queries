from collections import defaultdict


class KeyDefaultDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret


def sems_0(sems):
    return sems[0]


def sems_1(sems):
    return sems[1]


def sems_2(sems):
    return sems[2]


def sems_3(sems):
    return sems[3]


def merge_dicts(d1, d2):
    if not d2:
        return d1
    result = d1.copy()
    for k in d2.keys():
        if k in result:
            result.update({k + '_': d2[k]})
        else:
            result.update({k: d2[k]})
    return result


def convert_ner_date(sems):
    return sems[0]