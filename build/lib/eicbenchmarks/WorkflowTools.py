from eicbenchmarks import BenchmarkConfigurations as bc
from string import Template


def sim_cmds_to_flag(attribute, value):

    if attribute == bc.SIMULATION_DETECTOR_KEY:

        return "--compactFile $DETECTOR_PATH/{path}".format(path=value)
    
    if attribute == bc.SIMULATION_NUM_EVENTS_KEY:

        return "--numberOfEvents {num}".format(num=value)
    
    if attribute == bc.SIMULATION_ENABLE_GUN_KEY:

        if value:
            return "--enableGun"
        else:
            return ""
        
    if attribute == bc.SIMULATION_DISTRIBUTION_KEY:

        return "--gun.distribution {dist}".format(dist=value)
    
    if attribute == bc.SIMULATION_PARTCILE_KEY:

        return "--gun.partcile {part}".format(part=value)
    
    if attribute == bc.SIMULATION_MOMENTUM_MAX_KEY:

        return '--gun.momentumMax "{mom}"'.format(mom=value)
    
    if attribute == bc.SIMULATION_MOMENTUM_MIN_KEY:

        return '--gun.momentumMin "{mom}"'.format(mom=value)
    
    if attribute == bc.SIMULATION_THETA_MAX_KEY:

        return '--gun.thetaMax "{degree}"'.format(degree=value)

    if attribute== bc.SIMULATION_THETA_MIN_KEY:

        return '--gun.thetaMin "{degree}"'.format(degree=value)
    
    if attribute == bc.SIMULATION_ETA_MAX_KEY:

        return '--gun.etaMax "{eta}"'.format(eta=value)
    
    if attribute == bc.SIMULATION_ETA_MIN_KEY:

        return '--gun.etaMin "{eta}"'.format(eta=value)


def generate_sim_commands(common_config, sim_config):

    
    combined_config = dict(common_config.items() | sim_config.items())
    cmd_str = " "
    for k, v in combined_config.items():
        cmd_str += sim_cmds_to_flag(k, v) + " "
    
    return cmd_str
