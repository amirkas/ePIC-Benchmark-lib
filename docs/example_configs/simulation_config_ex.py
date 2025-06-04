from ePIC_benchmarks.simulation import SimulationConfig
from ePIC_benchmarks.simulation.simulation_types import GunDistribution, Particle

EXAMPLE_SIMULATION_CONFIG = SimulationConfig(
    num_events=10000,
    momentum="10GeV",
    distribution_type=GunDistribution.Eta,
    eta_min=-4,
    eta_max=4,
    particle=Particle.PionPlus,
    detector_xml="epic_craterlake_tracking_only.xml",
)