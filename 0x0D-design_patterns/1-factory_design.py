from abc import ABC, abstractmethod
import random

# Abstract Product
class SpaceProbe(ABC):
    @abstractmethod
    def launch(self):
        pass

    @abstractmethod
    def collect_data(self):
        pass

# Concrete Products
class SolarProbe(SpaceProbe):
    def __init__(self, probe_id):
        self.probe_id = probe_id
        self.energy_level = 100

    def launch(self):
        return f"Solar Probe {self.probe_id} launched towards the Sun"

    def collect_data(self):
        return f"Solar Probe {self.probe_id} collecting solar wind and radiation data"

class PlanetoProbe(SpaceProbe):
    def __init__(self, probe_id):
        self.probe_id = probe_id
        self.fuel_capacity = 500

    def launch(self):
        return f"Planetary Probe {self.probe_id} launched towards target planet"

    def collect_data(self):
        return f"Planetary Probe {self.probe_id} scanning planetary atmosphere and surface"

# Factory Class
class SpaceProbeFactory:
    _probe_counter = 0

    @classmethod
    def create_probe(cls, probe_type):
        """
        Create a space probe based on specified type.
        
        Args:
            probe_type (str): Type of space probe to create
        
        Returns:
            SpaceProbe: A new space probe instance
        
        Raises:
            ValueError: If an invalid probe type is specified
        """
        cls._probe_counter += 1
        
        if probe_type.lower() == 'solar':
            return SolarProbe(cls._probe_counter)
        elif probe_type.lower() == 'planet':
            return PlanetoProbe(cls._probe_counter)
        else:
            raise ValueError(f"Unknown probe type: {probe_type}")

# Demonstration
def mission_simulation():
    try:
        # Creating probes dynamically
        solar_probe = SpaceProbeFactory.create_probe('solar')
        planet_probe = SpaceProbeFactory.create_probe('planet')
        
        # Launch and data collection
        print(solar_probe.launch())
        print(solar_probe.collect_data())
        
        print(planet_probe.launch())
        print(planet_probe.collect_data())
        
        # This would raise an error
        invalid_probe = SpaceProbeFactory.create_probe('invalid')
    
    except ValueError as e:
        print(f"Mission Error: {e}")

if __name__ == "__main__":
    mission_simulation()