// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Bet} from "./Bet.sol";
import {User} from "./User.sol";
import {console} from "forge-std/Script.sol";

contract Totalizator {
    address private host;
    uint256 private bet_id;
    mapping(uint256 => User) private users;
    mapping(uint256 => Bet) private bets;

    modifier permition() {
        require(msg.sender == host, "Permition deniyed");
        _;
    }

    constructor() {
        host = msg.sender;
        users[0] = new User(host);
    }

    function createBet() external permition returns (uint256) {
        bet_id += 1;
        bets[bet_id] = new Bet();
        return bet_id;
    }

    function layBet(
        uint256 _bet_id,
        uint256 user_id,
        uint256 amount,
        bool choice
    ) public permition {
        require(_bet_id <= bet_id, "No such bet_id");
        users[user_id].layBet(_bet_id, amount, choice);
        bets[_bet_id].addBet(amount, user_id, choice);
    }

    function revertBet(uint256 _bet_id, uint256 user_id) public permition {
        (uint256 amount, bool choice) = users[user_id].revertBet(_bet_id);
        users[0].deposit(amount);
        bets[_bet_id].revertBet(amount, user_id, choice);
    }

    function finishBet(uint256 _bet_id, bool flag) public permition {
        require(_bet_id <= bet_id, "No such bet_id");
        Bet.retPayment[] memory payments = bets[bet_id].finishBet(flag);
        for (uint256 i = 0; i < payments.length; ++i) {
            users[payments[i].user].deposit(payments[i].amount);
        }
        delete bets[_bet_id];
    }

    function getRunningBets() external returns (uint32[] memory) {
        uint rt = 0;
        for (uint256 i = 1; i <= bet_id; ++i) {
            if (!bets[i].isFinished()) {
                ++rt;
            }
        }

        uint32[] memory running_bets = new uint32[](rt);
        rt = 0;
        for (uint256 i = 1; i <= bet_id; ++i) {
            if (!bets[i].isFinished()) {
                running_bets[rt] = uint32(i);
                ++rt;
            }
        }
        return running_bets;
    }

    function register(uint user_id, address user_address) external permition {
        require(address(users[user_id]) == address(0), "User exists");
        users[user_id] = new User(user_address);
    }

    function deposit(uint256 user_id) external payable {
        require(address(users[user_id]) != address(0), "User does not exist");
        users[user_id].deposit(msg.value);
    }

    function withdraw(uint256 user_id, uint256 amount) external permition {
        require(amount >= 10 gwei, "Too few amount");
        require(address(users[user_id]) != address(0), "User does not exist");

        uint256 total_amount = (101 * amount) / 100;
        users[user_id].withdraw(total_amount);
        users[0].deposit(total_amount - amount);
        payable(users[user_id].myUser()).transfer(amount);
    }

    function balanceOf(uint256 user_id) public view returns (uint256) {
        if (address(users[user_id]) == address(0)) {
            return 0;
        }
        return users[user_id].myBalance();
    }

    function getBet(uint256 _bet_id) public view returns (Bet) {
        require(_bet_id < bet_id, "No such bet");
        return bets[_bet_id];
    }
}
