from dataclasses import dataclass, fields, field
from epic_benchmarks.configurations._simulation._keys import SimulationKeyContainer, NPSIM_METADATA_KEY, EICRECON_METADATA_KEY
from epic_benchmarks.configurations._simulation.flags import NpsimExecutable, EicreconExecutable
from epic_benchmarks.configurations._config import BaseConfig


@dataclass
class SimulationConfig(BaseConfig):

    _config_key_container = SimulationKeyContainer()
    _is_common_config : bool = field(default=False, init=False)
    _npsim_exec : NpsimExecutable = field(default=NpsimExecutable(), init=False)
    _eicrecon_exec : EicreconExecutable = field(default=EicreconExecutable(), init=False)

    def npsimCommand(self, output_dir : str, output_file : str, compact_dir : str):

        output_npsim = self._npsim_exec.OutputFile


    def eicreconCommand(self, input_dir : str, input_file : str, output_dir : str, output_file : str, compact_dir : str):

        output_eicrecon = self._eicrecon_exec.OutputFile

    
    def _populate_npsim_exec(self):
        try:
            for key in self.keys():
                key_metadata = self.keyMetadata(key)
                if NPSIM_METADATA_KEY in key_metadata.keys():
                    key_flag = key_metadata[NPSIM_METADATA_KEY]
                    key_value = self.value(key)
                    self._npsim_exec.setFlagValue(key_flag, key_value)
        except Exception as e:
            raise e

    def _populate_eicrecon_exec(self):
        try:
            for key in self.keys():
                key_metadata = self.keyMetadata(key)
                if EICRECON_METADATA_KEY in key_metadata.keys():
                    key_flag = key_metadata[EICRECON_METADATA_KEY]
                    key_value = self.value(key)
                    self._npsim_exec.setFlagValue(key_flag, key_value)
        except Exception as e:
            raise e
        
    def __post_init__(self):


        #Additional validation

        #Populate npsim and eicrecon executable configurations
        self._populate_npsim_exec()
        self._populate_eicrecon_exec()


@dataclass
class CommonSimulationConfig(SimulationConfig):

    _is_common_config : bool = field(default=True, init=False)