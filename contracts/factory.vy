# @version 0.3.7
"""
@title Peredelano Escrow Factory
@license MIT
@author Maxson-dev
"""


interface Escrow:
    def approve_deal_terms(): nonpayable
    def deposit(): payable
    def confirm_service(): nonpayable
    def approve_receipt(): nonpayable
    def start_dispute(): nonpayable
    def refund_to_buyer(): nonpayable
    def payout_to_seller(): nonpayable
    def withdraw(): nonpayable
    def seller() -> address: view
    def buyer() -> address: view
    def arbiter() -> address: view
    def value() -> uint256: view
    def expired_at() -> uint256: view
    def status() -> Status: view


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

owner: public(address)

blueprint: public(address)

event EscrowCreated:
    contract: address
    seller: indexed(address)
    buyer: indexed(address)
    value: uint256
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
    return create_from_blueprint(
        self.blueprint,
        _seller, 
        _buyer,
        _arbiter, 
        _value, 
        _expiration_seconds,
        code_offset=3
    )
