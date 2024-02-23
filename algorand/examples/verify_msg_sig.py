from algosdk import account,  mnemonic, util
from algosdk.encoding import is_valid_address


def verify_signature(message, signature, public_address):
    return util.verify_bytes(message.encode('utf-8'), signature, public_address)


mnemonic_phrase = "twin pumpkin plastic stage fortune shallow melt betray ribbon receive claim enrich price exile absent avoid woman toilet print settle shiver inform rookie absorb unaware"
private_key = mnemonic.to_private_key(mnemonic_phrase)
public_address = account.address_from_private_key(private_key)

message = "Hello, Algorand!"
signature = util.sign_bytes(message.encode('utf-8'), private_key)
# false signature
#signature = "uezyrt+/Idm+TPLmtTALplnBQnYDqU2ECz4O+9AWIhccZ4eeIdplj9elBHXuLeLiZJc2dt+3n9KJrVp/hYnAw=="

print("Signature:", signature)

is_valid = verify_signature(message, signature, public_address)
print("Is the signature valid?", is_valid)

