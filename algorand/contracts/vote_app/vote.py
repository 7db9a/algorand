# This example is provided for informational purposes only and has not been audited for security.

from pyteal import *


def approval_program():
    on_creation = Seq([
        check_asa_holder(1),
        App.globalPut(Bytes("Creator"), Txn.sender()),
        Assert(Txn.application_args.length() == Int(1)), # Update argument count
        App.globalPut(Bytes("TotalSupply"), Btoi(Txn.application_args[0])), # Save TotalSupply in the global state
        Return(Int(1)),
    ])

    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    get_vote_of_sender = App.globalGetEx(Int(0), Concat(Bytes("Vote_"), Txn.sender()))

    on_closeout = Seq([
        get_vote_of_sender,
        If(
            get_vote_of_sender.hasValue(),
            App.globalPut(
                get_vote_of_sender.value(),
                App.globalGet(get_vote_of_sender.value()) - Int(1),
            ),
        ),
        Return(Int(1)),
    ])

    choice = Txn.application_args[1]
    choice_tally = App.globalGet(choice)

    asset_id = Int(1653) # Replace with your actual ASA ID

    balance = get_asa_balance_expr(asset_id)

    on_vote = Seq([
        check_asa_holder(1),
        If(check_winner_exists() == Int(0), Return(Int(0))),
        get_vote_of_sender,
        balance,
        If(get_vote_of_sender.hasValue(), Return(Int(0))),
        If(balance.hasValue(),
           Seq([
               If(
                   is_winner(choice_tally, balance.value(), 50),  # Check if 50% threshold is met
                   Seq([
                       App.globalPut(Bytes("Winner"), choice),  # Declare the winner
                       App.globalPut(choice, choice_tally + balance.value()),  # Update the tally
                   ]),
                   App.globalPut(choice, choice_tally + balance.value())  # Just update the tally
               ),
               App.globalPut(Concat(Bytes("Vote_"), Txn.sender()), choice),  # Record the vote
           ])
        ),
        Return(Int(1)),
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],  # Handle the OptIn logic
        [Txn.application_args[0] == Bytes("vote"), on_vote]
    )

    return program

def clear_state_program():
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))
    program = Seq([
        get_vote_of_sender,
        If(
            get_vote_of_sender.hasValue(),
            App.globalPut(
                get_vote_of_sender.value(),
                App.globalGet(get_vote_of_sender.value()) - Int(1),
            ),
        ),
        Return(Int(1)),
    ])

    return program

def get_asa_balance_expr(asset_id):
    balance = AssetHolding.balance(Txn.sender(), asset_id)
    return balance

def check_asa_holder(min_balance: int = 1):
    asset_id = Int(1653)
    balance = AssetHolding.balance(Txn.sender(), asset_id)
    return Seq([
        balance,
        Assert(balance.hasValue()),
        Assert(balance.value() >= Int(min_balance))
    ])

def is_winner(tally, balance, winning_percentage):
    totalSupply = App.globalGet(Bytes("TotalSupply"))
    winningThreshold = (totalSupply * Int(winning_percentage)) / Int(100)
    return tally + balance > winningThreshold

def check_winner_exists():
    winnerExistsVar = ScratchVar(TealType.uint64)
    winnerValueVar = ScratchVar(TealType.bytes)
    result = App.globalGetEx(Int(0), Bytes("Winner"))
    return Seq([
        result,
        winnerExistsVar.store(result.hasValue()),
        winnerValueVar.store(If(result.hasValue(), result.value(), Bytes(""))),
        If(
            And(
                winnerExistsVar.load(),
                winnerValueVar.load() != Bytes("")
            ),
            Int(0),  # A winner is declared, return 0 (False)
            Int(1)   # No winner yet, return 1 (True)
        )
    ])

if __name__ == "__main__":
    with open("vote_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=4)
        f.write(compiled)

    with open("vote_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=4)
        f.write(compiled)

