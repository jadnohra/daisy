from util.module import make_class_instance
from .road import Road
from .curve_builder import CurveBuilder
from .curve_resolver import CurveResolver


class RoadBuilder:
    def __init__(self):
        self.links = set()
        self.lanes = set()
        self.curve_builders = {}
        self.auto_id_counter = 0

    def gen_id(self):
        id = '#' + str(self.auto_id_counter)
        self.auto_id_counter = self.auto_id_counter + 1
        return id

    def ensure_id(self, id):
        return self.gen_id() if id is None else id

    def link(self, from_id, to_id):
        self.links.add((from_id, to_id))
        return self
        
    def lane(self, from_id, to_id):
        self.lanes.add((from_id, to_id))
        return self

    def curve(self, id=None):
        id = self.ensure_id(id)
        builder = CurveBuilder()
        builder.set_id(id)
        self.curve_builders[id] = builder
        return builder

    def load_and_build(self, road_module_or_file, params = {}):
        road_module = road_module_or_file
        module_actual_name, road_inst = make_class_instance('py_roads', road_module, 'Road')
        road_inst._build(self, params)
        road = self.build()
        road.description = road_inst.get_description()
        road.asciiart = road_inst.get_asciiart()
        road.param_descriptions = road_inst.get_param_descriptions()
        road.params = params
        road.source = module_actual_name
        return road

    def build(self):
        # Load curves, unresolved
        road = Road()
        self.curves = []
        self.curve_table = {}
        unresolved_curves = []
        # _print_road_ast(road_string)
        curve_table = {}
        for k, curve_builder in self.curve_builders.items():
            new_curve = CurveResolver(curve_builder)
            unresolved_curves.append(new_curve)
            curve_table[new_curve.id] = new_curve
        # Try to iteratively resolve curves, while some resolutions happen
        resolved_curves = []
        did_resolve_some_curves = True
        while len(unresolved_curves) != 0 and did_resolve_some_curves:
            resolved_curve_indices = []
            for i, unresolved_curve in enumerate(unresolved_curves):
                if unresolved_curve.resolve(curve_table) is not None:
                    resolved_curve_indices.append(i)
            did_resolve_some_curves = len(resolved_curve_indices) > 0
            for i in reversed(resolved_curve_indices):
                resolved_curves.append(unresolved_curves[i].get_resolved())
                unresolved_curves.pop(i)
        # Raise exception if not all curves could be resolved
        if len(unresolved_curves) != 0:
            raise Exception(f"Failed to resolve loaded road" 
                             + f"\n Resolved: {[x.id for x in resolved_curves]}"
                             + f"\n Unresolved: {[x.id for x in unresolved_curves]}")
        road.curves = resolved_curves
        for curve in road.curves:
            if curve.id is not None:
                road.curve_table[curve.id] = curve
        # Link curves
        for link in self.links:
            link_from, link_to = link[0], link[1]
            if link_from not in road.curve_table:
                raise Exception('Link from inexistent source: {}'.format(
                                link_from))
            if link_to not in road.curve_table:
                raise Exception('Link to inexistent target: {}'.format(
                                link_to))
            curve_from = road.curve_table[link_from]
            curve_to = road.curve_table[link_to]
            curve_from.add_outgoing_curve(curve_to)
            curve_to.add_incoming_curve(curve_from)
        # Lane curves
        for link in self.lanes:
            link_from, link_to = link[0], link[1]
            if link_from not in road.curve_table:
                raise Exception('Lane from inexistent source: {}'.format(
                                link_from))
            if link_to not in road.curve_table:
                raise Exception('Lane to inexistent target: {}'.format(
                                link_to))
            curve_from = road.curve_table[link_from]
            curve_to = road.curve_table[link_to]
            curve_from.add_outgoing_lane_curve(curve_to)
            curve_to.add_incoming_lane_curve(curve_from)
        return road