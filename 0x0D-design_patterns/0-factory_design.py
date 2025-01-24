from abc import ABC, abstractmethod

from virtual_accounts.services import VirtualAccountService


class IVirtualAccount(ABC):
    """
    # Inherits from ABC(Abstract Base Class).

    This is Interface from which all the different VirtualAccount are created
    it exposes one method create, which must be implemented by the concrete classes.
    """

    @abstractmethod  # Decorator to define an abstract method
    def create(self, user_obj):
        """
        This abstract method / interface, must be implemented in the concrete classes.
        """
        pass


class MonnifyVirtualAccount(IVirtualAccount):
    """
    Monnify.
    """

    def create(self, user_obj):
        VirtualAccountService.create_monnify_va(user_obj)


class PaystackVirtualAccount(IVirtualAccount):
    """
    Paystack.
    """

    def create(self, user_obj):
        VirtualAccountService.create_paystack_va(user_obj)


class FlutterwaveVirtualAccount(IVirtualAccount):
    """
    Flutterwave.
    """

    def create(self, user_obj):
        VirtualAccountService.create_flutterwave_va(user_obj)


class VirtualAccountFactory:
    """
    Virtual Account Factory that separates concrete class creation from use.
    """

    @staticmethod
    def get_provider_class(account_source):
        if account_source == "monnify":
            return MonnifyVirtualAccount
        if account_source == "paystack":
            return PaystackVirtualAccount
        if account_source == "flutterwave":
            return FlutterwaveVirtualAccount
        print(f"Invalid Provider <{provider}> Specified ")
        return None


if __name__=="__main__":
    users = [...]
    for user_obj in users:
        virtual_account_factory = VirtualAccountFactory.get_provider_class(user_obj.account_source)
        virtual_account_factory().create(user_obj)


    # On the flip side.
    VIRTUAL_ACCOUNT_TYPES = {"monnify":MonnifyVirtualAccount, "paystack":PaystackVirtualAccount, "flutterwave":FlutterwaveVirtualAccount}
    for user_obj in users:
        virtual_account_factory = VIRTUAL_ACCOUNT_TYPES.get(user_obj.account_source)
        virtual_account_factory().create(user_obj)