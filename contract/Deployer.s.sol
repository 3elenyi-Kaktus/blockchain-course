// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import {Script} from "../lib/forge-std/Script.sol";
import {Totalizator} from "Totalizator.sol";

contract DeployerScript is Script {
    Totalizator totalizator;
    uint256 my_pk;
    address payable me;

    function setUp() public {
        my_pk = vm.envUint("PRIVATE_KEY");
        me = payable(vm.addr(my_pk));
        console.log("My address:", me, "\n");
        vm.broadcast(my_pk);
        totalizator = new Totalizator();
        console.log("New instance address:", address(totalizator));
    }

    function run() public {
    }
}