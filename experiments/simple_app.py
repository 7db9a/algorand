from pyteal import *

def approval_program():
    return Approve()

# Generate TEAL Code
approval_program_teal = compileTeal(approval_program(), mode=Mode.Application, version=2)

# Save TEAL Code to File
with open("approval_program.teal", "w") as f:
    f.write(approval_program_teal)

