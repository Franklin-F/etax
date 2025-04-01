import json


class attrs:

    def __init__(self, attr_name='attr'):
        self.attr_name = attr_name

    def __set_name__(self, owner, name):
        self.key_name = name

    def __get__(self, obj, objtype=None):
        attr_val = self.get_attr_val(obj)
        return attr_val.get(self.key_name)

    def __set__(self, obj, value):
        attr_val = self.get_attr_val(obj)
        attr_val[self.key_name] = value
        self.set_attr_val(obj, attr_val)

    def __delete__(self, obj):
        attr_val = self.get_attr_val(obj)
        attr_val.pop(self.key_name, None)
        self.set_attr_val(obj, attr_val)

    def get_attr_val(self, obj):
        try:
            attr_val = getattr(obj, self.attr_name)
        except AttributeError:
            attr_val = None
        if not attr_val:
            attr_val = {}
        elif isinstance(attr_val, str):
            attr_val = json.loads(attr_val)
        return attr_val

    def set_attr_val(self, obj, attr_val):
        if not attr_val:
            setattr(obj, self.attr_name, None)
        else:
            setattr(obj, self.attr_name, json.dumps(attr_val, ensure_ascii=False))


class flags:

    def __init__(self, bit_offset, bit_num=1, attr_name='flag'):
        self.bit_offset = bit_offset
        self.bit_num = bit_num
        self.bit_mask = 2 ** bit_num - 1
        self.attr_name = attr_name

    def __get__(self, obj, objtype=None):
        attr_val = self.get_attr_val(obj)
        return (attr_val >> self.bit_offset) & self.bit_mask

    def __set__(self, obj, value):
        value = int(value)
        attr_val = self.get_attr_val(obj)
        attr_val &= ~(self.bit_mask << self.bit_offset)
        attr_val ^= (value << self.bit_offset)
        setattr(obj, self.attr_name, attr_val)

    def __delete__(self, obj):
        self.__set__(obj, 0)

    def get_attr_val(self, obj):
        try:
            attr_val = getattr(obj, self.attr_name)
        except AttributeError:
            attr_val = None
        if not attr_val:
            attr_val = 0
        else:
            attr_val = int(attr_val)
        return attr_val
