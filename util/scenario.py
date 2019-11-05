import random

def add_random_cars(scenario, car_count=10, seed=0, accel=40, min_speed=60, max_speed=90, component_names=[], creation_hook=None):
    rnd = random.Random(seed)
    car_count = int(car_count)
    for i in range(car_count):
        rgb = [x/255.0 for x in [rnd.randint(60,255), rnd.randint(40,255), rnd.randint(60,255)]]
        curve_idx = rnd.randint(0, len(scenario.road.curves)-1)
        curve_t = rnd.randint(0, 100) / 100.0
        builder = scenario.build_car().set_color(rgb) \
                            .set_acceleration(accel) \
                            .set_speed(min_speed + (float(i)/(car_count)) * (max_speed - min_speed) )

        for comp_name in component_names:
            builder.add_controller_by_name(comp_name)

        curve_idx = rnd.randint(0, len(scenario.road.curves)-1)
        curve_t = rnd.randint(0, 100) / 100.0
        car = builder.place(scenario.road.curves[curve_idx].id, curve_t)
        
        if creation_hook is not None:
            creation_hook(car)