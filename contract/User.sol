// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract UserBet {
    address owner;
    uint256 public id;
    uint256 public amount;
    bool public choice;

    modifier permition() {
        require(msg.sender == owner, "Permition deniyed");
        _;
    }

    constructor(uint256 _id, uint256 _amount, bool _choice) {
        owner = msg.sender;
        id = _id;
        amount = _amount;
        choice = _choice;
    }

    function clear() public permition {
        id = 0;
        amount = 0;
        choice = false;
    }
}

contract User {
    address admin;
    uint256 private balance;
    address private user;
    mapping(uint256 => UserBet) private bets;

    modifier permition() {
        require(msg.sender == admin, "Permition deniyed");
        _;
    }

    constructor(address _user) {
        admin = msg.sender;
        balance = 0;
        user = _user;
    }

    function layBet(
        uint256 bet_id,
        uint256 amount,
        bool choice
    ) public permition {
        require(bets[bet_id].id() != 0, "Bet is already laid");
        require(balance >= amount, "Not enough money");
        balance -= amount;
        bets[bet_id] = new UserBet(bet_id, amount, choice);
    }

    function revertBet(
        uint256 bet_id
    ) public permition returns (uint256, bool) {
        UserBet bet = bets[bet_id];
        require(bet.id() == 0, "Bet was not laid");
        uint256 amount = (9 * bets[bet_id].amount()) / 10;
        balance += amount;
        uint256 revert_commision = bets[bet_id].amount() - amount;
        bets[bet_id].clear();
        return (revert_commision, bet.choice());
    }

    function topUp(uint256 amount) public permition {
        balance += amount;
    }

    function withdraw(uint256 amount) public permition {
        balance -= amount;
    }

    function myBalance() public view returns (uint256) {
        return balance;
    }

    function myAddress() public view returns (address) {
        return user;
    }
}
