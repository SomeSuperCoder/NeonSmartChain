from Block import Block
from Blockchain import Blockchain
import utils

pk = utils.private_key_from_seed_phrase("")

blockchain = Blockchain()
block = blockchain.create_new_block([], pk)

print(block)

print(blockchain.validator.validate_block(block))
