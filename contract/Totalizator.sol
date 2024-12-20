// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Bet} from "./Bet.sol";
import {User} from "./User.sol";

contract Totalizator {
    address private host;
    uint256 private bet_id;
    mapping(uint256 => User) private users;
    mapping(uint256 => Bet) private bets;

    modifier permition() {
        require(msg.sender == host, "Permition deniyed");
        _;
    }

    constructor(address _host) {
        host = _host;
        users[0] = new User(host);
    }

    function createBet(
        string memory action_0,
        string memory action_1
    ) external permition {
        bet_id += 1;
        bets[bet_id] = new Bet(action_0, action_1);
    }

    function layBet(
        uint256 _bet_id,
        uint256 user_id,
        uint256 amount,
        bool choice
    ) public permition {
        require(_bet_id < bet_id, "No such bet_id");
        users[user_id].layBet(_bet_id, amount, choice);
        bets[_bet_id].addBet(amount, choice);
    }

    function revertBet(uint256 _bet_id, uint256 user_id) public permition {
        (uint256 amount, bool choice) = users[user_id].revertBet(_bet_id);
        users[0].topUp(amount);
        bets[_bet_id].revertBet(amount, choice);
    }

    function register(uint user_id, address user_address) external permition {
        require(users[user_id].myAddress() != address(0), "User exists");
        users[user_id] = new User(user_address);
    }

    function topUp(uint256 user_id, uint256 amount) external payable {
        require(
            users[user_id].myAddress() == address(0),
            "User does not exist"
        );
        users[user_id].topUp(amount);
    }

    function withdraw(uint256 user_id, uint256 amount) external payable {
        require(amount >= 10 gwei, "Too few amount");
        require(
            users[user_id].myAddress() == msg.sender,
            "Someone else's wallet"
        );
        uint256 total_amount = (101 * amount) / 100;
        require(users[user_id].myBalance() >= total_amount, "Not enough money");

        users[user_id].withdraw(total_amount);
        users[0].topUp(total_amount - amount);
        payable(msg.sender).transfer(amount);
    }

    function balanceOf(uint256 user_id) public view returns (uint256) {
        return users[user_id].myBalance();
    }
}
