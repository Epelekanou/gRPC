import random

def noisy(base, variance=1.0):
    return base + random.gauss(0, variance)

def occasional_spike(value, prob=0.05, magnitude=5):
    if random.random() < prob:
        return value + random.uniform(0, magnitude)
    return value

def temp_boiler_room():
    return noisy(random.uniform(60, 85), 1.5)

def temp_warehouse():
    return noisy(random.uniform(10, 30), 2.0)

def temp_assembly_line():
    base = random.uniform(25, 40)
    return occasional_spike(noisy(base, 1.0), 0.1, 5)

def temp_lab():
    return noisy(22, 0.3)


def humidity_boiler_room():
    return noisy(random.uniform(25, 45), 3)

def humidity_warehouse():
    return noisy(random.uniform(45, 65), 5)

def humidity_assembly_line():
    return noisy(random.uniform(40, 60), 4)

def humidity_lab():
    return noisy(40, 1.5)


def vibration_assembly_line():
    base = random.uniform(0.2, 0.6)
    return occasional_spike(base, 0.15, 1.5)

def vibration_boiler_room():
    base = random.uniform(0.1, 0.3)
    return occasional_spike(base, 0.08, 0.8)

def vibration_warehouse():
    base = random.uniform(0.05, 0.2)
    return occasional_spike(base, 0.1, 1.0)

def vibration_lab():
    return random.uniform(0.01, 0.05)


GENERATOR_MAP = {
    ("temperature", "boiler_room"): temp_boiler_room,
    ("temperature", "warehouse"): temp_warehouse,
    ("temperature", "assembly_line"): temp_assembly_line,
    ("temperature", "lab"): temp_lab,

    ("humidity", "boiler_room"): humidity_boiler_room,
    ("humidity", "warehouse"): humidity_warehouse,
    ("humidity", "assembly_line"): humidity_assembly_line,
    ("humidity", "lab"): humidity_lab,

    ("vibration", "boiler_room"): vibration_boiler_room,
    ("vibration", "warehouse"): vibration_warehouse,
    ("vibration", "assembly_line"): vibration_assembly_line,
    ("vibration", "lab"): vibration_lab,
}