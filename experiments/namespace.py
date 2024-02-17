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

    # Handling different transaction types
    program = Cond(
        [Txn.application_id() == Int(0), on_initialization],
        [Txn.application_args[0] == Bytes("update"), on_update],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)]  # Allow deletion by the creator
    )

    return compileTeal(program, mode=Mode.Application, version=3)

def clear_state_program():
    program = Seq([
        Return(Int(1))
    ])

    return compileTeal(program, mode=Mode.Application, version=3)

if __name__ == "__main__":
    with open("namespace_approval.teal", "w") as f:
        compiled = approval_program()
        f.write(compiled)

    with open("namespace_clear_state.teal", "w") as f:
        compiled = clear_state_program()
        f.write(compiled)

