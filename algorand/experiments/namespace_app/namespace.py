from pyteal import *

def approval_program():
    on_initialization = Seq([
        App.globalPut(Bytes("Creator"), Txn.sender()),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(Bytes("RepoName"), Txn.application_args[0]),
        App.globalPut(Bytes("RepoURL"), Txn.application_args[1]),
        Return(Int(1))
    ])

    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    on_update = Seq([
        Assert(is_creator),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(Bytes("RepoName"), Txn.application_args[0]),
        App.globalPut(Bytes("RepoURL"), Txn.application_args[1]),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_initialization],
        [Txn.application_args[0] == Bytes("update"), on_update],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)]
    )

    return program

def clear_state_program():
    return Seq([
        Return(Int(1))
    ])

if __name__ == "__main__":
    # Compile the approval program
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=2)
    with open("namespace_approval_program.teal", "w") as f:
        f.write(approval_teal)

    # Compile the clear state program
    clear_state_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=2)
    with open("namespace_clear_state_program.teal", "w") as f:
        f.write(clear_state_teal)