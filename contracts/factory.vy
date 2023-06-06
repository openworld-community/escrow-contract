# @version 0.3.7
"""
@title Peredelano Escrow Factory
@license MIT
@author Maxson-dev
"""

import escrow as Escrow 

enum Status:
    # покупатель создал сделку и ждет апрува от продавца
    WAIT_SELLER_APPROVE 
    # продавец создал сделку | заапрувил созданную покупателем сделку
    WAIT_BUYER_DEPOSIT
    # покупатель сделал депозит и ждет выполнения условий сделки
    WAIT_SELLER_SERVICE
    # продавец подтвердил, что выполнил условия сделки и ждет аппрува от покупателя
    WAIT_BUYER_APPROVE
    # покупатель не согласен с тем что условия сделки выполнены, исход решает арбитр
    DISPUT
    # сделка завершена
    DONE

owner: address

blueprint: public(address)

event EscrowCreated:
    contract: address
    buyer: indexed(address)
    seller: indexed(address)
    value: indexed(uint256)
    expiration_time: uint256


@external
def __init__(_blueprint: address):
    self.blueprint = _blueprint
    self.owner = msg.sender


@external
def create_escrow(
    _seller: address,
    _buyer: address, 
    _arbiter: address,
    _value: uint256, 
    _expiration_seconds: uint256
) -> address:

    escrow_addr: address = create_from_blueprint(
        self.blueprint,
        _seller, 
        _buyer,
        _arbiter, 
        _value, 
        _expiration_seconds, 
        code_offset=len("FE7100")
    )

    log EscrowCreated(escrow_addr, _buyer, _seller, _value, _expiration_seconds)

    return escrow_addr