from typing import Sequence 

def concatenate_commands(*commands : Sequence[str]):

    return ' && '.join(commands)