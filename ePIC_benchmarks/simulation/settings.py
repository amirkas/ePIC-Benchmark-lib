# from pydantic_settings import BaseSettings, InitSettingsSource, CliPositionalArg, CliImplicitFlag, CliExplicitFlag, CliSubCommand, CliApp
# from pydantic import Field
# from typing import Optional

# class SimulationSettings(BaseSettings, cli_enforce_required=True, cli_prog_name='npsim', cli_flag_prefix_char='-'):

#     num_events : Optional[int] = Field(default=100)
#     particle : Optional[str] = Field(default="pi+")
#     # gun_enabled : CliImplicitFlag[bool] = True

# test = SimulationSettings()

# test_source = InitSettingsSource(test, init_kwargs={})

# print(test_source.current_state)

# print(str(test))
# print(test.model_dump_json())


