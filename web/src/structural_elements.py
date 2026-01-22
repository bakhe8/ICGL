from typing import List

class StructuralElement:
    def __init__(self, id: str, length: float, material: str):
        self.id = id
        self.length = length
        self.material = material

class Beam(StructuralElement):
    def __init__(self, id: str, length: float, material: str, cross_section_area: float):
        super().__init__(id, length, material)
        self.cross_section_area = cross_section_area

class Column(StructuralElement):
    def __init__(self, id: str, length: float, material: str, load_capacity: float):
        super().__init__(id, length, material)
        self.load_capacity = load_capacity