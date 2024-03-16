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
    choice = Txn.application_args[1]
    choice_tally = App.globalGet(choice)

    get_vote_of_sender = App.globalGetEx(Int(0), Concat(Bytes("Vote_"), choice, Bytes("_"), Txn.sender()))

    on_closeout = Seq([
        get_vote_of_sender,
        If(
            get_vote_of_sender.hasValue(),
            Return(Int(0)),
        ),
        Return(Int(1)),
    ])

    asset_id = Int(1653) # Replace with your actual ASA ID

    balance = get_asa_balance_expr(asset_id)

    choice_existence = choice_existence_check(choice)
    #original_voter_exists_check = choice_existence_check(Concat(Bytes("OriginalVoter_"), choice, Txn.sender()))
    original_voter_exists_check = compare_global_value(
        Concat(Bytes("OriginalVoter_"), choice),
        Txn.sender()
    )
    on_vote = Seq([
        check_asa_holder(1),
        If(check_winner_exists() == Int(0), Return(Int(0))),
        get_vote_of_sender,
        balance,
        If(balance.hasValue(),
            Seq([
                # Check if a winner exists and the user is trying to vote on a different choice
                #(winner := App.globalGetEx(Int(0), Bytes("Winner"))),
                #If(winner.hasValue(),
                #    If(winner.value() != choice,
                #        Seq([
                #            App.globalPut(Bytes("LastWinner"), winner.value()),
                #            App.globalDel(Bytes("Winner"))
                #        ])
                #    )
                #),
                # Record first (original) voter and track.
                If(choice_existence == Int(0),
                    Seq([
                        App.globalPut(Concat(Bytes("OriginalVoter_"), choice), Txn.sender()),
                    ])
                ),
                # If the choice either does not exist or the voter is the original, then proceed
                If(Or(choice_existence == Int(0), original_voter_exists_check == Int(1)),
                    Seq([
                        # Only set <choice>_child if the choice doesn't exist or if it does exist
                        App.globalPut(Concat(choice, Bytes("_child")), Txn.application_args[2]),
                    ])
                ),
                # Check if a choice is already marked as "Exclusive"
                (exclusive_value := App.globalGetEx(Int(0), Bytes("Exclusive"))),
                If(exclusive_value.hasValue(),
                    Seq([
                        # If a choice is already marked as "Exclusive", check if the current choice matches the "Exclusive" choice
                        If(exclusive_value.value() == choice,
                            Seq([
                                # If the current choice matches the "Exclusive" choice, allow the vote
                                # Tally is updated only if this is the first time the sender is voting for this choice
                                If(
                                    Not(get_vote_of_sender.hasValue()),
                                    App.globalPut(choice, choice_tally + balance.value())
                                ),
                                # Check for winner after updating tally
                                If(
                                    is_milestone(choice_tally, 50),
                                    Seq([
                                        App.globalPut(Bytes("Winner"), choice),
                                        App.globalPut(Bytes("WinnerRef"), App.globalGet(Concat(choice, Bytes("_child")))),
                                        # If a winner is declared, delete the "Exclusive" key
                                        App.globalDel(Bytes("Exclusive"))
                                    ]),
                                ),
                                # Record the vote regardless of whether it's a repeat vote or not
                                App.globalPut(Concat(Bytes("Vote_"), choice, Bytes("_"), Txn.sender()), Int(1))
                            ]),
                            # If the current choice doesn't match the "Exclusive" choice, reject the vote
                            Seq([
                                Assert(Int(0), comment="The chosen option is not the exclusive choice."),
                                Err()
                            ])
                        )
                    ]),
                    # If no choice is marked as "Exclusive", proceed with the regular voting process
                    Seq([
                        # Tally is updated only if this is the first time the sender is voting for this choice
                        If(
                            Not(get_vote_of_sender.hasValue()),
                            App.globalPut(choice, choice_tally + balance.value())
                        ),
                        # Check for winner after updating tally
                        If(
                            is_milestone(choice_tally, 50),
                            Seq([
                                App.globalPut(Bytes("Winner"), choice),
                                App.globalPut(Bytes("WinnerRef"), App.globalGet(Concat(choice, Bytes("_child")))),
                                # If a winner is declared, delete the "Exclusive" key if it exists
                                If(exclusive_value.hasValue(),
                                    App.globalDel(Bytes("Exclusive"))
                                )
                            ]),
                        ),
                        # Check for exclusive vote only if a winner hasn't been declared
                        If(
                            And(
                                is_milestone(choice_tally, 10),
                                Not(compare_global_value(Bytes("Winner"), choice)) # Compare the "Winner" value with the current choice
                            ),
                            App.globalPut(Bytes("Exclusive"), choice),
                        ),
                        # Record the vote regardless of whether it's a repeat vote or not
                        App.globalPut(Concat(Bytes("Vote_"), choice, Bytes("_"), Txn.sender()), Int(1))
                    ])
                )
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
        [Txn.application_args[0] == Bytes("vote"), on_vote],
        [Txn.application_args[0] == Bytes("delete_key"), delete_key_branch()]
    )

    return program

def clear_state_program():
    #get_vote_of_sender = App.globalGetEx(Int(0), Concat(Concat(Concat(Bytes("Vote_"), Txn.sender()), Bytes("_")), choice))
    program = Seq([
    #    get_vote_of_sender,
    #    If(
    #        get_vote_of_sender.hasValue(),
    #        Return(Int(0))
    #    ),
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

def is_milestone(tally, winning_percentage):
    totalSupply = App.globalGet(Bytes("TotalSupply"))
    winningThreshold = (totalSupply * Int(winning_percentage)) / Int(100)
    return tally >= winningThreshold

def choice_existence_check(choice):
    result = App.globalGetEx(Int(0), choice)

    return Seq([
        result,
        If(result.hasValue(),
           Int(1),  # Choice exists, return 1 (True)
           Int(0)   # Choice does not exist, return 0 (False)
        )
    ])

def compare_global_value(key, value_to_compare):
    result = App.globalGetEx(Int(0), key)

    return Seq([
        result,
        If(result.hasValue(),
           If(BytesEq(result.value(), value_to_compare),
              Int(1),  # Value matches, return 1 (True)
              Int(0)   # Value does not match, return 0 (False)
           ),
           Int(0)   # Key does not exist, return 0 (False)
        )
    ])


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

def delete_key_branch():
    # Ensure that there are enough arguments and the sender is the creator
    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))
    key_to_delete = Txn.application_args[1]
    return Seq([
        Assert(Txn.application_args.length() == Int(2)),
        Assert(is_creator),
        App.globalDel(key_to_delete),
        Return(Int(1))  # Ensure successful completion
    ])

if __name__ == "__main__":
    with open("vote_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=4)
        f.write(compiled)

    with open("vote_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=4)
        f.write(compiled)

