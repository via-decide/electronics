from dataclasses import dataclass
@dataclass(frozen=True)
class Geometry:
    dies:int; blocks_per_die:int; pages_per_block:int; page_size:int; spare_size:int
    @property
    def page_count(self): return self.dies*self.blocks_per_die*self.pages_per_block
