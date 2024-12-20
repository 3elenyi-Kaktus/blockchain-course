// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract Bet {
    address private admin;
    uint256 private amount_0;
    uint256 private amount_1;

    string public action_0;
    string public action_1;

    constructor(string memory _action_0, string memory _action_1) public {
        admin = msg.sender;
        amount_0 = 1;
        amount_1 = 1;
        action_0 = _action_0;
        action_1 = _action_1;
    }

    function countCoefficients() public view returns (uint256, uint256) {
        require(amount_0 > 0 && amount_1 > 0, "Invalid amounts in Bet");
        uint256 total = amount_0 + amount_1;
        return (total / amount_0, total / amount_1);
    }

    function addBet(uint256 amount, bool choice) public {
        require(msg.sender == admin, "Permission denied");
        if (choice) {
            amount_0 += amount;
        } else {
            amount_1 += amount;
        }
    }

    function revertBet(uint256 amount, bool choice) public {
        require(msg.sender == admin, "Permission denied");
        if (choice) {
            amount_0 -= amount;
        } else {
            amount_1 -= amount;
        }
    }
}
