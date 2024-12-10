from dataclasses import dataclass


@dataclass
class Range:
    Max = 0
    Min = 0
    ValueName = "Value"
    ValueUnits = ""

    @classmethod
    def validate(cls, val):
        if val < cls.Min or val > cls.Max:
            raise Exception(f"Value for {cls.ValueName}, '{val}{cls.ValueUnits}', must be in the range: [{cls.Min}, {cls.Max}]")
        
    @classmethod
    def inRange(cls, val):
        try:
            cls.validate(float(val))
        except:
            return False
        return True
    
    @classmethod
    def __repr__(cls):
        return f"{cls.ValueName} has units {cls.ValueUnits} and range [{cls.Max}, {cls.Min}]"