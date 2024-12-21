// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {console} from "forge-std/Script.sol";

contract UserBet {
    uint256 public user_id;
    uint256 public amount;
    bool public choice;
    bool public canceled;

    constructor(
        uint256 _user_id,
        uint256 _amount,
        bool _choice,
        bool _canceled
    ) {
        user_id = _user_id;
        amount = _amount;
        choice = _choice;
        canceled = _canceled;
    }
}

contract Bet {
    address private admin;
    uint256 private amount_0;
    uint256 private amount_1;
    bool private finished;

    function isFinished() public view returns (bool) {
        return finished;
    }

    UserBet[] participants;

    modifier permition() {
        require(msg.sender == admin, "Permission denied");
        _;
    }

    constructor() public {
        admin = msg.sender;
        amount_0 = 1;
        amount_1 = 1;
    }

    function countCoefficients()
        public
        view
        permition
        returns (uint256, uint256)
    {
        return (amount_0, amount_1);
    }

    function addBet(
        uint256 amount,
        uint256 user_id,
        bool choice
    ) public permition {
        if (choice) {
            amount_0 += amount;
        } else {
            amount_1 += amount;
        }

        participants.push(new UserBet(user_id, amount, choice, false));
    }

    function revertBet(
        uint256 amount,
        uint256 user_id,
        bool choice
    ) public permition {
        if (choice) {
            amount_0 -= amount;
        } else {
            amount_1 -= amount;
        }

        participants.push(new UserBet(user_id, amount, choice, true));
    }
    struct retPayment {
        uint256 user;
        uint256 amount;
    }

    function finishBet(bool winner_flag) public permition returns (retPayment[] memory) {
        require(!finished, "Finished already");
        finished = true;

        uint parts = 0;
        for (uint256 i = 0; i < participants.length; ++i) {
            if (!participants[i].canceled() && participants[i].choice() == winner_flag) {
                ++parts;
            }
        }

        retPayment[] memory payments = new retPayment[](parts);
        parts = 0;

        uint mul = winner_flag ? amount_1 : amount_0;
        uint div = winner_flag ? amount_0 : amount_1;
        console.log("Mul", mul);
        console.log("Div", div);

        for (uint256 i = 0; i < participants.length; ++i) {
            if (participants[i].canceled()) {
                continue;
            }
            if (participants[i].choice() == winner_flag) {
                console.log("Base", participants[i].amount());
                console.log("Add", participants[i].amount() * mul / div);
                console.log("Fin", participants[i].amount() + participants[i].amount() * mul / div);
                payments[parts] = retPayment(participants[i].user_id(), participants[i].amount() + participants[i].amount() * mul / div);
                ++parts;
            }
        }
        return payments;
    }
}
