from telnetlib import DO
import pytest
from brownie import escrow as Escrow, factory as Factory, accounts, web3, network, chain, reverts, Contract

network.connect("development")

"""
@dev vyper enum members are represented by uint256 values 
in the form of 2n where n is the index of the member in the range 0 <= n <= 255.
"""
WAIT_SELLER_APPROVE = 1
WAIT_BUYER_DEPOSIT = 2
WAIT_SELLER_SERVICE = 4
WAIT_BUYER_APPROVE = 8
DISPUT = 16
DONE = 32

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

SELLER = accounts[1]
BUYER = accounts[2]
ARBITER = accounts[3]
VALUE = 100000000
EXPIRATION_SECONDS = 86400

FAIL = 'failed preconditions'
DEPOSIT_FAILURE = "buyer must deposit full value of deal"


@pytest.fixture
def blueprint():
    yield accounts[0].deploy(Escrow, accounts[0], accounts[0], accounts[0], 0, 0)


@pytest.fixture
def factory(blueprint):
    yield accounts[0].deploy(Factory, blueprint)


def test_factory_init_state(factory, blueprint):
    assert factory.owner() == accounts[0]
    assert factory.blueprint() == blueprint


@pytest.fixture
def buyer_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': BUYER})


def test_buyer_escrow(buyer_escrow):
    be = buyer_escrow
    assert be.buyer() == BUYER
    assert be.seller() == SELLER
    assert be.arbiter() == ARBITER
    assert be.expired_at() == chain[-1].timestamp + EXPIRATION_SECONDS
    assert be.value() == VALUE
    assert be.status() == WAIT_SELLER_APPROVE
    with reverts(FAIL):
        be.approve_deal_terms({'from': BUYER})
    with reverts(FAIL):
        be.approve_deal_terms({'from': ARBITER})

    seller_approve_tx = be.approve_deal_terms({'from': SELLER})
    assert be.status() == WAIT_BUYER_DEPOSIT

    check_status_transition(
        WAIT_SELLER_APPROVE,
        WAIT_BUYER_DEPOSIT,
        SELLER,
        seller_approve_tx.events
    )

    with reverts(FAIL):
        be.deposit({'from': SELLER, 'value': VALUE})
    with reverts(DEPOSIT_FAILURE):
        be.deposit({'from': BUYER, 'value': VALUE-1})

    buyer_deposit_tx = be.deposit({'from': BUYER, 'value': VALUE})
    assert be.balance() == VALUE
    assert be.status() == WAIT_SELLER_SERVICE

    check_status_transition(
        WAIT_BUYER_DEPOSIT,
        WAIT_SELLER_SERVICE,
        BUYER,
        buyer_deposit_tx.events
    )

    revert_all_withdraw(be)

    with reverts(FAIL):
        be.confirm_service({'from': BUYER})
    with reverts(FAIL):
        be.confirm_service({'from': ARBITER})

    seller_confirm_service_tx = be.confirm_service({'from': SELLER})
    assert be.status() == WAIT_BUYER_APPROVE
    assert be.balance() == VALUE

    check_status_transition(
        WAIT_SELLER_SERVICE,
        WAIT_BUYER_APPROVE,
        SELLER,
        seller_confirm_service_tx.events
    )

    revert_all_withdraw(be)

    with reverts(FAIL):
        be.approve_receipt({'from': SELLER})
    with reverts(FAIL):
        be.approve_receipt({'from': ARBITER})

    old_seller_balance = SELLER.balance()
    old_escrow_balance = be.balance()

    buyer_approve_receipt_tx = be.approve_receipt({'from': BUYER})
    assert be.status() == DONE
    assert be.balance() == old_escrow_balance - VALUE
    assert SELLER.balance() == old_seller_balance + VALUE

    check_status_transition(
        WAIT_BUYER_APPROVE,
        DONE,
        BUYER,
        buyer_approve_receipt_tx.events
    )

    revert_all_withdraw(be)


def revert_all_withdraw(be):
    with reverts(FAIL):
        be.withdraw({'from': BUYER})
    with reverts(FAIL):
        be.withdraw({'from': SELLER})
    with reverts(FAIL):
        be.withdraw({'from': ARBITER})


def check_status_transition(s_from, s_to, actor, evts):
    assert len(evts) == 1
    assert evts[0]['status_from'] == s_from
    assert evts[0]['status_to'] == s_to
    assert evts[0]['actor'] == actor


@pytest.fixture
def seller_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': SELLER})

def test_seller_escrow(seller_escrow):
    se = seller_escrow
    assert se.buyer() == BUYER
    assert se.seller() == SELLER
    assert se.arbiter() == ARBITER
    assert se.expired_at() == chain[-1].timestamp + EXPIRATION_SECONDS
    assert se.value() == VALUE
    assert se.status() == WAIT_BUYER_DEPOSIT
    with reverts(FAIL):
        se.deposit({"from": SELLER, "value": VALUE})
    with reverts(DEPOSIT_FAILURE):
        se.deposit({"from": BUYER, "value": VALUE-1})
    
    buyer_deposit_tx = se.deposit({"from": BUYER, "value": VALUE})
    assert se.balance() == VALUE
    assert se.status() == WAIT_SELLER_SERVICE

    check_status_transition(
        WAIT_BUYER_DEPOSIT,
        WAIT_SELLER_SERVICE,
        BUYER,
        buyer_deposit_tx.events
    )

    revert_all_withdraw(se)

    with reverts(FAIL):
        se.confirm_service({"from": BUYER})
    with reverts(FAIL):
        se.confirm_service({"from": ARBITER})
    
    seller_confirm_service_tx = se.confirm_service({"from": SELLER})
    assert se.status() == WAIT_BUYER_APPROVE
    assert se.balance() == VALUE

    check_status_transition(
        WAIT_SELLER_SERVICE,
        WAIT_BUYER_APPROVE,
        SELLER,
        seller_confirm_service_tx.events
    )

    revert_all_withdraw(se)

    with reverts(FAIL):
        se.approve_receipt({"from": SELLER})
    with reverts(FAIL):
        se.approve_receipt({"from": ARBITER})
    
    old_escrow_balance = se.balance()
    old_seller_balance = SELLER.balance()

    buyer_approve_receipt_tx = se.approve_receipt({"from": BUYER})
    assert SELLER.balance() == old_seller_balance + VALUE
    assert se.status() == DONE
    assert se.balance() == old_escrow_balance - VALUE
    check_status_transition(
        WAIT_BUYER_APPROVE,
        DONE,
        BUYER,
        buyer_approve_receipt_tx.events
    )
    
    revert_all_withdraw(se)

"""Withdraw test"""

@pytest.fixture
def seller_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': SELLER})

def test_withdraw_no_buyer(seller_escrow):
    se = seller_escrow
    buyer_deposit_tx = se.deposit({"from": BUYER, "value": VALUE})

    revert_all_withdraw(se)

    seller_confirm_service_tx = se.confirm_service({"from": SELLER})

    revert_all_withdraw(se)

    assert se.status() == WAIT_BUYER_APPROVE

    old_escrow_balance = se.balance()
    old_seller_balance = SELLER.balance()

    chain.sleep(EXPIRATION_SECONDS) 
    chain.mine(web3.eth.blockNumber + 1)
    assert chain[-1].timestamp >= se.expired_at()

    with reverts(FAIL):
        se.withdraw({"from": BUYER})
    with reverts(FAIL):
        se.withdraw({"from": ARBITER})
    
    seller_withdraw_tx = se.withdraw({"from": SELLER})

    assert SELLER.balance() == old_seller_balance + VALUE
    assert se.status() == DONE
    assert se.balance() == old_escrow_balance - VALUE

    check_status_transition(
        WAIT_BUYER_APPROVE,
        DONE,
        SELLER,
        seller_withdraw_tx.events
    )


@pytest.fixture
def buyer_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': BUYER})

def test_withdraw_no_arbiter(buyer_escrow):
    be = buyer_escrow

    seller_approve_tx = be.approve_deal_terms({'from': SELLER})

    buyer_deposit_tx = be.deposit({"from": BUYER, "value": VALUE})

    revert_all_withdraw(be)

    seller_confirm_service_tx = be.confirm_service({"from": SELLER})

    revert_all_withdraw(be)

    with reverts(FAIL):
        be.start_dispute({"from": SELLER})
    with reverts(FAIL):
        be.start_dispute({"from": ARBITER})

    buyer_start_dispute_tx = be.start_dispute({"from": BUYER})

    revert_all_withdraw(be)

    assert be.status() == DISPUT
    check_status_transition(
        WAIT_BUYER_APPROVE,
        DISPUT,
        BUYER,
        buyer_start_dispute_tx.events
    )

    old_escrow_balance = be.balance()
    old_seller_balance = SELLER.balance()

    chain.sleep(EXPIRATION_SECONDS) 
    chain.mine(web3.eth.blockNumber + 1)
    assert chain[-1].timestamp >= be.expired_at()

    with reverts(FAIL):
        be.withdraw({"from": BUYER})
    with reverts(FAIL):
        be.withdraw({"from": ARBITER})
    
    seller_withdraw_tx = be.withdraw({"from": SELLER})

    assert SELLER.balance() == old_seller_balance + VALUE
    assert be.status() == DONE
    assert be.balance() == old_escrow_balance - VALUE

    check_status_transition(
        DISPUT,
        DONE,
        SELLER,
        seller_withdraw_tx.events
    )

"""Dispute test"""

@pytest.fixture
def buyer_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': BUYER})

def test_refund_to_buyer(buyer_escrow):
    be = buyer_escrow

    seller_approve_tx = be.approve_deal_terms({'from': SELLER})

    buyer_deposit_tx = be.deposit({"from": BUYER, "value": VALUE})

    seller_confirm_service_tx = be.confirm_service({"from": SELLER})

    with reverts(FAIL):
        be.start_dispute({"from": SELLER})
    with reverts(FAIL):
        be.start_dispute({"from": ARBITER})

    buyer_start_dispute_tx = be.start_dispute({"from": BUYER})
    assert be.status() == DISPUT

    revert_all_withdraw(be)

    check_status_transition(
        WAIT_BUYER_APPROVE,
        DISPUT,
        BUYER,
        buyer_start_dispute_tx.events
    )

    old_escrow_balance = be.balance()
    old_buyer_balance = BUYER.balance()

    with reverts(FAIL):
        be.refund_to_buyer({"from": BUYER})
    with reverts(FAIL):
        be.refund_to_buyer({"from": SELLER})

    refund_to_buyer_tx = be.refund_to_buyer({"from": ARBITER})

    assert be.status() == DONE
    assert BUYER.balance() == old_buyer_balance + VALUE
    assert be.balance() == old_escrow_balance - VALUE

    check_status_transition(
        DISPUT,
        DONE,
        ARBITER,
        refund_to_buyer_tx.events
    )

@pytest.fixture
def buyer_escrow():
    yield Escrow.deploy(SELLER, BUYER, ARBITER, VALUE, EXPIRATION_SECONDS, {'from': BUYER})

def test_payout_to_seller(buyer_escrow):
    be = buyer_escrow

    seller_approve_tx = be.approve_deal_terms({'from': SELLER})

    buyer_deposit_tx = be.deposit({"from": BUYER, "value": VALUE})

    seller_confirm_service_tx = be.confirm_service({"from": SELLER})

    with reverts(FAIL):
        be.start_dispute({"from": SELLER})
    with reverts(FAIL):
        be.start_dispute({"from": ARBITER})

    buyer_start_dispute_tx = be.start_dispute({"from": BUYER})
    assert be.status() == DISPUT

    revert_all_withdraw(be)

    check_status_transition(
        WAIT_BUYER_APPROVE,
        DISPUT,
        BUYER,
        buyer_start_dispute_tx.events
    )

    old_escrow_balance = be.balance()
    old_seller_balance = SELLER.balance()

    with reverts(FAIL):
        be.payout_to_seller({"from": BUYER})
    with reverts(FAIL):
        be.payout_to_seller({"from": SELLER})
    
    payout_to_seller_tx = be.payout_to_seller({"from": ARBITER})

    assert be.status() == DONE
    assert SELLER.balance() == old_seller_balance + VALUE
    assert be.balance() == old_escrow_balance - VALUE

    check_status_transition(
        DISPUT,
        DONE,
        ARBITER,
        payout_to_seller_tx.events
    )
