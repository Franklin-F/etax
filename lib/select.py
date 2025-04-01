import itertools
import collections.abc
from django.db.models import Max, Min, F, Q


REPR_OUTPUT_SIZE = 20


class select:
    def __init__(self, cls,
                 id=None,
                 ids=None,
                 minid=None,
                 maxid=None,
                 slice=None,
                 reverse=None,
                 limit=None,
                 where=None,
                 chunk=1000,
                 pk=None,
                 **kwargs
                 ):
        self.cls = cls
        self.id = id
        self.ids = ids
        self.minid = minid
        self.maxid = maxid
        self.slice = slice
        self.reverse = reverse
        self.limit = limit
        self.where = where
        self.chunk = chunk
        self.pk = pk or 'id'
        self.filters = kwargs

        self._result_cache = None

    def __repr__(self):
        if self._result_cache is None:
            self._result_cache = self.get_models()
        data = list(self._result_cache[: REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return "<%s %r>" % (self.cls.__name__, data)

    def __bool__(self):
        if self._result_cache is None:
            self._result_cache = self.get_models()
        return bool(self._result_cache)

    def __len__(self):
        if self._result_cache is None:
            self._result_cache = self.get_models()
        return len(self._result_cache)

    def __iter__(self):
        if self._result_cache is not None:
            return iter(self._result_cache)
        return iter(self.gen_model())

    def get_models(self):
        return list(self.gen_model())

    def gen_model(self):
        yield from itertools.islice(
            itertools.chain.from_iterable(self.gen_query()),
            self.limit,
        )

    def gen_query(self):
        if self.id is not None:
            yield from self.gen_id_query()
            return

        query = self.cls.objects.all()
        if self.ids:
            query = query.filter(pk__in=self.ids)
        if self.minid:
            query = query.filter(pk__gte=self.minid)
        if self.maxid:
            query = query.filter(pk__lte=self.maxid)
        if self.filters:
            query = self.parse_filters(query)
        if self.where:
            query = self.parse_where(query)
        if self.slice:
            divider, remainder = self.slice.split(',')
            query = query.annotate(idmod=F(self.pk) % int(divider)).filter(idmod=int(remainder))
        if self.reverse:
            query = query.order_by('-pk')
        if self.limit:
            query = query[:self.limit]

        if not self.chunk:
            yield query
            return

        if self.maxid and self.maxid <= self.chunk:
            yield query
            return

        if self.minid is None and self.maxid is None:
            ids = query.aggregate(minid=Min(self.pk), maxid=Max(self.pk))
            minid = ids['minid'] or 0
            maxid = ids['maxid'] or 0
        elif self.minid is None:
            ids = query.aggregate(minid=Min(self.pk))
            minid = ids['minid'] or 0
            maxid = self.maxid
        elif self.maxid is None:
            minid = self.minid
            ids = query.aggregate(maxid=Max(self.pk))
            maxid = ids['maxid'] or 0
        else:
            minid = self.minid
            maxid = self.maxid

        if maxid - minid < self.chunk:
            yield query
            return

        if self.reverse:
            start = maxid
            end = minid - 1
            step = -self.chunk
            bottom = step + 1
            top = 0
        else:
            start = minid
            end = maxid + 1
            step = self.chunk
            bottom = 0
            top = step - 1

        for i in range(start, end, step):
            if query.query.is_sliced:
                query.query.clear_limits()
            new_query = query.filter(
                pk__gte=max(minid, i+bottom),
                pk__lte=min(maxid, i+top),
            )
            if self.limit:
                new_query = new_query[:self.limit]
            yield new_query

    def gen_id_query(self):
        if isinstance(self.id, int):
            pks = [self.id]
        elif isinstance(self.id, str) and self.id.lower().startswith('select '):
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(self.id)
                pks = [row[0] for row in cursor.fetchall()]
        elif isinstance(self.id, str):
            pks = [int(pk) for pk in self.id.split(',')]
        elif isinstance(self.id, collections.abc.Sequence):
            pks = list(self.id)
        else:
            raise ValueError('Invalid id should be int str list tuple')

        pks = set(pks)
        if not pks:
            return

        query = self.cls.objects.all()
        query = query.filter(pk__in=pks)
        yield query

    def parse_filters(self, query):
        fields = set(field.name for field in self.cls._meta.get_fields())
        filters = {key: val for key, val in self.filters.items() if key in fields}
        if not filters:
            return query
        query = query.filter(**filters)
        return query

    def parse_where(self, query):
        import sqltree
        from sqltree.parser import NullExpression, Parenthesized, BinOp, Identifier, NumericLiteral

        def tov(n):
            if isinstance(n, NumericLiteral):
                if n.value.isdigit():
                    return int(n.value)
                return float(n.value)
            return n.value

        def toa(n):
            if isinstance(n, Parenthesized):
                n = n.inner
            rv = tov(n.right)
            if n.op.text == '&':
                key = f'{n.left.text}_bitand_{rv}'
                val = F(n.left.text).bitand(rv)
            elif n.op.text == '|':
                key = f'{n.left.text}_bitor_{rv}'
                val = F(n.left.text).bitor(rv)
            elif n.op.text == '<<':
                key = f'{n.left.text}_bitleftshift_{rv}'
                val = F(n.left.text).bitleftshift(rv)
            elif n.op.text == '>>':
                key = f'{n.left.text}_bitrightshift_{rv}'
                val = F(n.left.text).bitrightshift(rv)
            elif n.op.text == 'XOR':
                key = f'{n.left.text}_bitxor_{rv}'
                val = F(n.left.text).bitxor(rv)
            elif n.op.text == '+':
                key = f'{n.left.text}_add_{rv}'
                val = F(n.left.text) + rv
            elif n.op.text == '-':
                key = f'{n.left.text}_sub_{rv}'
                val = F(n.left.text) - rv
            elif n.op.text == '*':
                key = f'{n.left.text}_mul_{rv}'
                val = F(n.left.text) * rv
            elif n.op.text == '/':
                key = f'{n.left.text}_div_{rv}'
                val = F(n.left.text) / rv
            elif n.op.text == '%':
                key = f'{n.left.text}_mod_{rv}'
                val = F(n.left.text) % rv
            else:
                raise ValueError('Do no support op %s' % n)
            return key, val

        def toqa(n):
            a = {}
            if isinstance(n, Parenthesized):
                n = n.inner
            if n.op.text in ('AND', 'OR'):
                lq, la = toqa(n.left)
                rq, ra = toqa(n.right)
                a.update(la)
                a.update(ra)
                q = lq & rq if n.op.text == 'AND' else lq | rq
                return q, a

            if isinstance(n.left, Identifier):
                key = n.left.text
            elif isinstance(n.left, (BinOp, Parenthesized)):
                key, val = toa(n.left)
                a[key] = val
            else:
                raise ValueError('Invalid left size value %s' % n)

            if n.op.text == '=':
                kw = {f'{key}__exact': n.right.value}
            elif n.op.text == '!=' or n.op.text == '<>':
                kw = {f'{key}__ne': n.right.value}
            elif n.op.text == '>':
                kw = {f'{key}__gt': n.right.value}
            elif n.op.text == '>=':
                kw = {f'{key}__gte': n.right.value}
            elif n.op.text == '<':
                kw = {f'{key}__lt': n.right.value}
            elif n.op.text == '<=':
                kw = {f'{key}__lte': n.right.value}
            elif n.op.text == 'LIKE':
                kw = {f'{key}__like': n.right.value}
            elif n.op.text == 'NOT LIKE':
                kw = {f'{key}__nolike': n.right.value}
            elif n.op.text == 'IN':
                kw = {f'{key}__in': [tov(n.node) for n in n.right.exprs]}
            elif n.op.text == 'NOT IN':
                kw = {f'{key}__noin': [tov(n.node) for n in n.right.exprs]}
            elif n.op.text == 'IS' and isinstance(n.right, NullExpression):
                kw = {f'{key}__isnull': True}
            elif n.op.text == 'IS NOT' and isinstance(n.right, NullExpression):
                kw = {f'{key}__isnull': False}
            else:
                raise ValueError('Do not support sql contains %s' % n)
            return Q(**kw), a

        if not self.where:
            return query
        s = 'select * from tmp where ' + self.where
        stmt = sqltree.sqltree(s)
        q, a = toqa(stmt.where.conditions)
        if a:
            query = query.annotate(**a)
        if q:
            query = query.filter(q)
        return query
