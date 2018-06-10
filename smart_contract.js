/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* global getAssetRegistry getFactory emit */

/**
 * Sample transaction processor function.
 * @transaction
 * @param {org.example.basic.expenseTransaction} tx The sample transaction instance.
 */
async function expenseTransaction(tx) {  // eslint-disable-line no-unused-vars


    //if transaction is from trader
    if (tx.from.trade == 1) {

        if (tx.asset.expectedReturns >= getAssetReturn(tx)) {

            tx.asset.owner = tx.to;
            tx.to.balance = tx.to.balance + tx.asset.expectedReturns;
            tx.from.balance = tx.from.balance - tx.asset.expectedReturns;

        }

    }



    const expectedReturns = tx.asset.returns;
    const from = tx.from;
    const to = tx.to;

    // Update the asset with the new value.




    tx.asset.owner = to;


    //After Trading Commision
    const balanceAfterTradeCommision = await tradeCommision(tx.value);


    tx.from.balance = tx.from.balance - tx.value;

    //After Trader Commision
    const balanceAfterTraderCommision = await traderCommision(balanceAfterTradeCommision);

    //Asset Value after all commision
    tx.asset.value = balanceAfterTraderCommision;

    //Trader balance updated
    tx.to.balance = tx.to.balance + balanceAfterTraderCommision;

    // Get the asset registry for the asset.
    const assetRegistry = await getAssetRegistry('org.example.basic.expenseAsset');
    // Update the asset in the asset registry.
    await assetRegistry.update(tx.asset);

    const userRegistry = await getParticipantRegistry('org.example.basic.Users');
    await userRegistry.update(tx.to);
    await userRegistry.update(tx.from);

    // Emit an event for the modified asset.
    /*let event = getFactory().newEvent('org.example.basic', 'SampleEvent');
    event.asset = tx.asset;
    event.oldValue = oldValue;
    event.newValue = tx.newValue;
    emit(event); */
}


async function traderCommision(amount) {

    //rating logic and calc commision
    amount = amount - amount * 0.02;
    return amount;

}

async function tradeCommision(amount) {

    amount = amount - amount * 0.05;

    return amount;

}

//TODO
//Traders return after investing and current worth


async function traderPortfolio(amount) {

    //get the current portfolio

    //TODO
    //Need to figure out how to get current portfolio
    const stakeAmount = 1000;
    const totalPortfolio = 200000;
    const totalStake = amount / stakeAmount;
    const profit = totalPortfolio - amount;
    const profitPerStake = profit / totalStake;
    return profitPerStake;

}


async function getAssetReturn(tx) {

    const profitPerStake = traderPortfolio(tx.from.balance);

    const profit = (tx.asset.value / tx.asset.stakeValue) * profitPerStake;
    return profit;


}







