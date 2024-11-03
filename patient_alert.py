from dataclasses import dataclass

@dataclass
class PatientAlert:
   priority: int  # 0-10
   reason: str
   excerpt: str
   
   def __post_init__(self):
       if not 0 <= self.priority <= 10:
           raise ValueError("Priority must be between 0 and 10")