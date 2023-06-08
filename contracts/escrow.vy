# @version 0.3.7
"""
@title Peredelano Escrow Contract
@license MIT
@author Maxson-dev
"""

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

event StatusTransition:
    status_from: indexed(Status)
    status_to: indexed(Status)
    actor: address

seller: public(address)
buyer: public(address)
arbiter: public(address)

value: public(uint256)

expired_at: public(uint256)

status: public(Status)


@external
def __init__(
    _seller: address, 
    _buyer: address, 
    _arbiter: address, 
    _value: uint256,
    _expiration_seconds: uint256
):
    assert msg.sender == _buyer or msg.sender == _seller, "Escrow can be created only by buyer or seller!"

    if msg.sender == _buyer:
        # если покупатель создал сделку, он ждет аппрува от продавца 
        self.status = Status.WAIT_SELLER_APPROVE
    else:
        # если продавец создал сделку, он ждет депозита средств от покупателя
        self.status = Status.WAIT_BUYER_DEPOSIT

    self.seller = _seller
    self.buyer = _buyer
    self.arbiter = _arbiter
    self.expired_at = block.timestamp + _expiration_seconds
    self.value = _value


@external
def approve_deal_terms():
    """ 
    @notice продавец подтверждает условия сделки и ожидает депозита от покупателя
    """
    assert self.status == Status.WAIT_SELLER_APPROVE and msg.sender == self.seller, "failed preconditions"
    self.status = Status.WAIT_BUYER_DEPOSIT

    log StatusTransition(Status.WAIT_SELLER_APPROVE, Status.WAIT_BUYER_DEPOSIT, msg.sender)


@external 
@payable
def deposit():
    """ 
    @notice покупатель вносит депозит на контракт и ожидает выполнения условий сделки от продавца
    """
    assert self.status == Status.WAIT_BUYER_DEPOSIT and msg.sender == self.buyer, "failed preconditions"
    assert msg.value == self.value, "buyer must deposit full value of deal"
    self.status = Status.WAIT_SELLER_SERVICE

    log StatusTransition(Status.WAIT_BUYER_DEPOSIT, Status.WAIT_SELLER_SERVICE, msg.sender)


@external
def confirm_service():
    """
    @notice продавец подтверждает оказание услуги и ожидает аппрува от покупателя
    """
    assert self.status == Status.WAIT_SELLER_SERVICE and msg.sender == self.seller, "failed preconditions"
    self.status = Status.WAIT_BUYER_APPROVE

    log StatusTransition(Status.WAIT_SELLER_SERVICE, Status.WAIT_BUYER_APPROVE, msg.sender)


@external
def approve_receipt():
    """
    @notice покупатель подтверждает факт оказания услуги и продавец получает средства
    """
    assert self.status == Status.WAIT_BUYER_APPROVE and msg.sender == self.buyer, "failed preconditions"
    send(self.seller, self.value)
    self.status = Status.DONE

    log StatusTransition(Status.WAIT_BUYER_APPROVE, Status.DONE, msg.sender)


# DISPUT

@external 
def start_dispute():
    """
    @notice покупатель не согласен с тем, что условия сделки выполнены и открывает спор. 
    Далее исход сделки решает арбитр
    """
    assert self.status == Status.WAIT_BUYER_APPROVE and msg.sender == self.buyer, "failed preconditions"
    self.status = Status.DISPUT

    log StatusTransition(Status.WAIT_BUYER_APPROVE, Status.DISPUT, msg.sender)


@external
def refund_to_buyer():
    """
    @notice арбитр решает спор в пользу покупателя и сделка завершается.
    """
    assert self.status == Status.DISPUT and msg.sender == self.arbiter, "failed preconditions"
    send(self.buyer, self.value)
    self.status = Status.DONE

    log StatusTransition(Status.DISPUT, Status.DONE, msg.sender)

@external
def payout_to_seller():
    """
    @notice арбитр решает спор в пользу продавца и сделка завершается.
    """
    assert self.status == Status.DISPUT and msg.sender == self.arbiter, "failed preconditions"
    send(self.seller, self.value)
    self.status = Status.DONE

    log StatusTransition(Status.DISPUT, Status.DONE, msg.sender)

@external 
@nonreentrant("lock")
def withdraw():
    """
    @notice продавец выводит средства с контракта за истечением срока сделки.
    """
    assert msg.sender == self.seller and self.expired_at <= block.timestamp, "failed preconditions"
    assert self.status == Status.WAIT_BUYER_APPROVE or self.status == Status.DISPUT, "failed preconditions"
    old_status: Status = self.status
    send(self.seller, self.value)
    self.status = Status.DONE

    log StatusTransition(old_status, Status.DONE, msg.sender)

