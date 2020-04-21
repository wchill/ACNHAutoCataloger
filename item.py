class Item:

    def __init__(self, name):
        self.name = name
        self.variants = set()

    def add_variant(self, variant):
        self.variants.add(variant)

    def has_variant(self, variant):
        return variant in self.variants

    @property
    def __dict__(self):
        return {
            'name': self.name,
            'variants': list(self.variants)
        }

    def __str__(self):
        if len(self.variants) > 0:
            return f'{self.name}: {" / ".join(self.variants)}'
        else:
            return self.name
