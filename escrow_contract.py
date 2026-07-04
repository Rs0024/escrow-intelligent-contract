from genlayer import IntelligentContract, Field, event


class EscrowContract(IntelligentContract):
    """
    Escrow Intelligent Contract
    ----------------------------
    Holds funds sent by a buyer and releases them to the seller
    only when the agreed condition is confirmed. If the condition
    is not met, the buyer can request a refund.
    """

    buyer = Field(address=True)
    seller = Field(address=True)
    amount = Field(int, default=0)
    condition_met = Field(bool, default=False)
    funds_released = Field(bool, default=False)

    @event
    def initialize(self, buyer, seller, amount):
        """Set up the escrow with buyer, seller, and locked amount."""
        self.buyer = buyer
        self.seller = seller
        self.amount = amount
        self.condition_met = False
        self.funds_released = False

    @event
    def confirm_condition(self):
        """Buyer confirms that the agreed condition has been fulfilled."""
        assert self.sender == self.buyer, "Only the buyer can confirm the condition"
        assert not self.funds_released, "Funds have already been released"
        self.condition_met = True

    @event
    def release_funds(self):
        """Release the escrowed funds to the seller once condition is met."""
        assert self.condition_met, "Condition has not been met yet"
        assert not self.funds_released, "Funds already released"
        self.transfer(self.seller, self.amount)
        self.funds_released = True

    @event
    def refund(self):
        """Refund the buyer if the condition was never met."""
        assert self.sender == self.buyer, "Only the buyer can request a refund"
        assert not self.condition_met, "Cannot refund after condition is met"
        assert not self.funds_released, "Funds already released"
        self.transfer(self.buyer, self.amount)
        self.funds_released = True
