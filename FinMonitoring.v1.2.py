""" Financial monitoring. v1.2 """

from json import load, dump  # (storing / loading) data (from / to) .json file.
from json.decoder import JSONDecodeError as JsonDE  # catching a loading data mistake.

from prettytable import PrettyTable as PtT  # making tables for the display.

#  yf is used making graphs and collecting information (financial sector)
import yfinance as yf

#  dt is used for making a set of date used for building graphs and analysing assets.
import datetime as dt

#  Those libraries imported for making graph and working with financial parameters.
import pandas_datareader as web
import mplfinance as mpf

#  Those libraries imported for making graph for more than two companies.
import matplotlib.pyplot as plt
import pandas as pnd

#  This library used for making hit maps.
import seaborn as sns


class Bank:
    def __init__(self, name):
        self.name = name  # str : a name of a Bank() object.
        self.bank = []  # is an array of assets for management : [Asset(), ]
        self.messages = []  # is an array of messages from assets from [bank].

    def __str__(self):
        return f"{len(self)} {'asset' if len(self) == 1 else 'assets'} " \
               f"in '{self.name}'"

    def __len__(self):
        return len(self.bank)

    def loading_assets_data_from_json_file_to_the_bank_array(self, file_name):
        """ self_portfolio.json, other_portfolio.json, watchlist.json """
        with open(file_name, "r") as json_bank_of_assets_file:
            loaded_data = load(json_bank_of_assets_file)

            if len(loaded_data) != 0:
                for ticker, parameter in loaded_data.items():
                    asset = Asset(ticker, parameter["type"], parameter["currency"])

                    asset.dividends = parameter["dividends"]
                    asset.costs = parameter["costs"]

                    asset.quantity = parameter["quantity"]
                    asset.worth_of_one = parameter["worth of 1"]
                    asset.worth_of_all = parameter["worth of all"]

                    asset.comments = parameter["comments"]
                    asset.strategies = parameter["strategies"]
                    self.bank.append(asset)

    def saving_information_from_the_bank_array_to_json_file(self, file_name):
        with open(file_name, "w") as json_bank_of_assets_file:
            saved_data = {}

            for asset in self.bank:
                saved_data[asset.ticker] = {
                    "type": asset.asset_type, "currency": asset.currency,
                    "dividends": asset.dividends, "costs": asset.costs,
                    "quantity": asset.quantity, "worth of 1": asset.worth_of_one,
                    "worth of all": asset.worth_of_all,
                    "comments": asset.comments, "strategies": asset.strategies
                }

            dump(saved_data, json_bank_of_assets_file)

    def sending_news_about_messages_to_the_display(self):
        self.a_current_and_wish_price_comparing_function()
        if len(self.messages) != 0:
            print(f"There are {len(self.messages)} "
                  f"{'message' if len(self.messages) == 1 else 'messages'} "
                  f"from '{self.name}'.")
        else:
            print(f"There are no messages from '{self.name}'.")

    def a_current_and_wish_price_comparing_function(self):
        for asset in self.bank:
            for name, parameter in asset.strategies.items():

                if asset.price <= parameter["WP buy"]:
                    self.a_message_maker(
                        asset, name, "less", "buying", parameter["WP buy"])

                if asset.price >= parameter["WP sell"]:
                    self.a_message_maker(
                        asset, name, "more", "selling", parameter["WP sell"])

    def a_message_maker(self, asset, strategy, difference, action, value):
        self.messages.append(
            f"Ticker: {asset.ticker} with the '{strategy}' strategy:\nCurrent "
            f"price {asset.price} {asset.currency} is {difference} than wish "
            f"price for {action} of the asset: {value} {asset.currency}.\n"
        )

    def sending_all_messages_to_the_display(self):
        if len(self.messages) >= 1:
            print(*self.messages, sep="\n")

    def adding_a_new_asset_or_a_new_strategy(self):
        asset = Asset.making_a_new_asset_or_returning_an_exist_asset(self)
        if asset:
            asset.making_a_new_asset_strategy(self.name)
            if asset not in self.bank:
                self.bank.append(asset)

    def deleting_the_asset_from_the_bank(self):
        deleting_flag = True
        while deleting_flag:
            ticker = input("\nWhat asset do you want to delete: ").upper()

            if any(ticker == asset.ticker for asset in self.bank):
                for asset in self.bank:
                    if ticker == asset.ticker:
                        print(f"{asset.ticker} was deleted.")
                        del self.bank[self.bank.index(asset)]
            else:
                print(f"This asset is not in '{self.name}'.")
                deleting_flag = a_small_navigation_after_some_functions(
                    "try again", "again", "quit")
                continue

            deleting_flag = a_small_navigation_after_some_functions(
                "delete other asset", "else", "quit")

    def showing_the_bank_on_the_display(self):
        if "Portfolio" in self.name:
            table = self.making_a_table_for_the_bank_with_portfolio_in_the_name()
        else:
            table = self.making_a_table_for_the_bank_with_watchlist_in_the_name()

        print()
        print(table, end="\n\n")

    def making_a_table_for_the_bank_with_portfolio_in_the_name(self):
        table = PtT(padding_width=2)
        bank_worth, bank_dividends, bank_costs = 0, 0, 0
        bank_today, bank_delta = 0, 0

        table.field_names = [
            "Ticker", "Type", "Today", "Worth of all", "Delta", "%", "Quantity",
            "Worth of 1", "Currency", "Dividends", "Costs", "WP buy", "WP sell"
        ]

        for asset in self.bank:
            bank_worth += asset.worth_of_all
            bank_dividends += asset.dividends
            bank_costs += asset.costs

        for asset in self.bank:
            wish_price_buy, wish_price_sell = \
                self.returning_the_most_and_least_wish_prices(asset)

            delta = (asset.price * asset.quantity) - asset.worth_of_all
            bank_delta += delta
            bank_today += (asset.price * asset.quantity)

            table.add_row([
                asset.ticker, asset.asset_type, str(asset.price),
                str(asset.worth_of_all), str(round(delta, 2)),
                str(round((asset.worth_of_all * 100 / bank_worth), 2)),
                str(asset.quantity), str(asset.worth_of_one),
                str(asset.currency), str(asset.dividends),
                str(asset.costs), str(wish_price_buy), str(wish_price_sell)
            ])

        table.add_row([
            "all", "", str(round(bank_today, 2)), str(round(bank_worth, 2)),
            str(round(bank_delta, 2)), "100", "", "", "",
            str(round(bank_dividends, 2)), str(round(bank_costs, 2)), "", ""
        ])

        return table

    @staticmethod
    def returning_the_most_and_least_wish_prices(asset):
        wish_price_buy, wish_price_sell = float("inf"), 0

        for strategy in asset.strategies:
            if wish_price_buy > asset.strategies[strategy]["WP buy"]:
                wish_price_buy = asset.strategies[strategy]["WP buy"]

            if wish_price_sell < asset.strategies[strategy]["WP sell"]:
                wish_price_sell = asset.strategies[strategy]["WP sell"]

        return wish_price_buy, wish_price_sell

    def making_a_table_for_the_bank_with_watchlist_in_the_name(self):
        table = PtT(padding_width=2)
        table.field_names = ["Ticker", "Type", "Today",
                             "Currency", "WP buy", "WP sell"]

        for asset in self.bank:
            wish_price_buy, wish_price_sell = \
                self.returning_the_most_and_least_wish_prices(asset)

            table.add_row([
                asset.ticker, asset.asset_type, str(asset.price), asset.currency,
                str(wish_price_buy), str(wish_price_sell)
            ])

        return table

    def a_function_for_changing_something_inside_the_asset(self):
        change_flag = True
        while change_flag:
            asset = self.check_if_an_item_is_in_the_bank(
                input("\nPrint a ticker of an asset: ").upper())

            if not asset:
                print("This asset is not exist in the bank. Please, try again.")
                change_flag = a_small_navigation_after_some_functions(
                    "try again", "change", "quit")
                continue
            else:
                print()
                print(asset)
                change = input("\nPick from [ticker, type, currency, dividends, "
                               "costs, comments, strategy, quit]: ").lower()

                if change == "ticker":
                    asset.change_a_ticker_of_the_asset()

                elif change == "type":
                    asset.change_a_type_of_the_asset()

                elif change == "currency":
                    asset.change_a_currency_of_the_asset()

                elif change == "dividends":
                    asset.change_a_dividend_value_of_the_asset()

                elif change == "costs":
                    asset.change_a_costs_value_of_the_asset()

                elif change == "comments":
                    asset.change_comments_of_the_asset()

                elif change == "strategy":
                    print()
                    print(f"{asset.ticker} >>> strategies:\n" +
                          "\n".join(f"{stt} : {value}" for
                                    stt, value in asset.strategies.items()))

                    print()
                    asset.change_a_strategy_and_all_inside_of_it_of_the_asset(
                        string_parser(
                            asset.ticker, "strategy ", asset.strategies.keys()))

                elif change == "quit" or change == "exit":
                    change_flag = False
                    continue

                else:
                    print(f"{change} command doesn't exist.")

            change_flag = a_small_navigation_after_some_functions(
                "change other asset", "else", "done")

    def check_if_an_item_is_in_the_bank(self, ticker):
        for asset in self.bank:
            if ticker == asset.ticker:
                return asset
        return None


class Asset:
    def __init__(self, ticker, asset_type, currency):
        self.ticker = ticker  # str.upper() : ticker of the asset.
        self.asset_type = asset_type  # str.lower() : in [stock, crypto, bond].
        self.currency = currency  # str.upper() : currency of the asset.

        self.price = self.getting_a_current_price_of_an_asset()  # float : price today.

        self.dividends = 0  # float : number of dividends from this asset.
        self.costs = 0  # float : number of costs from this asset.
        self.quantity = 0  # float : quantity of assets in the bank.

        self.worth_of_one = 0  # float : median worth of 1 asset in the bank.
        self.worth_of_all = 0  # float : self.quantity * self.worth_of_one.

        self.comments = ""  # str : comments about this asset.
        self.strategies = {}  # dict : contain all purchases and wish prices.

    def __str__(self):
        return f"{self.ticker} ({self.asset_type}): {self.price} {self.currency}" + \
               "\n" + f"dividends: {self.dividends} {self.currency}, costs: " \
                      f"{self.costs} {self.currency}" + "\n" + \
               "\n".join(f"{strategy} : {value}" for
                         strategy, value in self.strategies.items())

    def getting_a_current_price_of_an_asset(self):
        return round(float(yf.Ticker(self.ticker).history(
            period="1d")["Close"][0]), 2) if \
            self.asset_type in ("stock", "bond") else \
            round(float(yf.Ticker(f"{self.ticker}-{self.currency}").history(
                period="1d")["Close"][0]), 2)

    @staticmethod
    def making_a_new_asset_or_returning_an_exist_asset(bank):
        ticker = input("\nPlease, print a ticker of an asset: ").upper()

        for asset in bank.bank:
            if ticker == asset.ticker:
                return asset
        else:
            type_of_an_asset = string_parser(
                ticker, "Please, print a type of an asset: ",
                ["stock", "crypto", "bond"])
            currency = input(f"{ticker} >>> Please, print a currency name "
                             f"for this asset: ").upper()
            return Asset(ticker, type_of_an_asset, currency)

    def making_a_new_asset_strategy(self, place):
        strategy = self.returning_strategy_name_if_not_in_the_self_strategy()

        if "Portfolio" in place:
            self.strategies[strategy] = {"Purchases": {}, "WP buy": 0, "WP sell": 0}

            self.adding_all_purchases_to_the_portfolio(strategy)
            self.calculating_worth_and_quantity_of_the_asset()
            self.dividends_and_costs_maker(strategy)
        else:
            self.strategies[strategy] = {"WP buy": 0, "WP sell": 0}

        self.wish_price_for_buying_and_selling_and_comments_maker(strategy)

    def returning_strategy_name_if_not_in_the_self_strategy(self):
        print()
        print(f"{self.ticker} >>> Names of the strategies: " +
              ", ".join(name for name in self.strategies.keys()))

        while True:
            strategy = input(f"{self.ticker} >>> Please, print a "
                             "name of a strategy: ").lower()

            if strategy in [name for name in self.strategies.keys()]:
                print(f"\nThis name '{strategy}' is already exist. Please, try again.")
            else:
                return strategy

    def adding_all_purchases_to_the_portfolio(self, strategy):
        flag = True
        while flag:
            quantity = checking_if_an_input_is_a_number(
                input(f"{self.ticker} >>> {strategy} >>> How much assets did "
                      f"you buy (same price): "))

            price = str(checking_if_an_input_is_a_number(
                input(f"{self.ticker} >>> {strategy} >>> What was the price "
                      f"of the asset: ")))

            if price in self.strategies[strategy]["Purchases"]:
                self.strategies[strategy]["Purchases"][price] += quantity
            else:
                self.strategies[strategy]["Purchases"][price] = quantity

            flag = a_small_navigation_after_some_functions(
                "add a new pare", "add", "done")

    def calculating_worth_and_quantity_of_the_asset(self):
        quantity_overall, worth_overall = 0, 0

        for value in self.strategies.values():
            for price, quantity in value["Purchases"].items():
                quantity_overall += float(quantity)
                worth_overall += (float(price) * float(quantity))

        self.quantity = round(quantity_overall, 2)
        self.worth_of_all = round(worth_overall, 2)
        self.worth_of_one = round((worth_overall / quantity_overall), 2)

    def dividends_and_costs_maker(self, strategy):
        self.dividends += checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> "
                  f"How much dividends did you obtain: "))

        self.costs += checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> "
                  f"How much costs did you pay: "))

    def wish_price_for_buying_and_selling_and_comments_maker(self, strategy):
        self.strategies[strategy]["WP buy"] += checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> What is a wish price"
                  f" for buying: "))

        self.strategies[strategy]["WP sell"] += checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> What is a wish price"
                  f" for selling: "))

        self.comments = input(f"{self.ticker} >>> Comments: ")

    def change_a_ticker_of_the_asset(self):
        self.ticker = input(f"{self.ticker} >>> Print a new ticker "
                            f"for the asset: ").upper()
        self.price = self.getting_a_current_price_of_an_asset()
        print(f"New ticker is {self.ticker}: {self.price} {self.currency}.")

    def change_a_type_of_the_asset(self):
        self.asset_type = input(f"{self.ticker} >>> Print a new type "
                                f"of the asset: ").lower()
        print(f"New type of the asset {self.ticker}: {self.asset_type}.")

    def change_a_currency_of_the_asset(self):
        self.currency = input(f"{self.ticker} >>> Print a new currency "
                              f"of the asset: ").upper()
        print(f"New currency of the asset {self.ticker}: {self.currency}.")

    def change_a_dividend_value_of_the_asset(self):
        print(f"{self.ticker} >>> dividends >>> {self.dividends} {self.currency}")
        dividends_changer = input(f"{self.ticker} >>> dividends >>> [+, =]: ")

        if dividends_changer in ("+", "p", "plus"):
            self.dividends += checking_if_an_input_is_a_number(
                input(f"plus >>> Your number: "), message=self.ticker)
            print(f"New dividends of the asset {self.ticker}: "
                  f"{self.dividends} {self.currency}.")

        elif dividends_changer in ("=", "e", "equal"):
            self.dividends = checking_if_an_input_is_a_number(
                input(f"equal >>> Your number: "), message=self.ticker)
            print(f"New dividends of the asset {self.ticker}: "
                  f"{self.dividends} {self.currency}.")

        else:
            print(f"'{dividends_changer}' command doesn't exist.")

    def change_a_costs_value_of_the_asset(self):
        print(f"{self.ticker} >>> costs >>> {self.costs} {self.currency}")
        costs_changer = input(f"{self.ticker} >>> costs >>> [+, =]: ")

        if costs_changer in ("+", "p", "plus"):
            self.costs += checking_if_an_input_is_a_number(
                input(f"plus >>> Your number: "), message=self.ticker)
            print(f"New costs of the asset {self.ticker}: "
                  f"{self.costs} {self.currency}.")

        elif costs_changer in ("=", "e", "equal"):
            self.costs = checking_if_an_input_is_a_number(
                input(f"equal >>> Your number: "), message=self.ticker)
            print(f"New costs of the asset {self.ticker}: "
                  f"{self.costs} {self.currency}.")

        else:
            print(f"'{costs_changer}' command doesn't exist.")

    def change_comments_of_the_asset(self):
        print(f"{self.ticker} >>> comments:\n'{self.comments}'\n")
        self.comments = input(f"{self.ticker} >>> comments >>> New comment: ")

    def change_a_strategy_and_all_inside_of_it_of_the_asset(self, strategy):
        print(f"{self.ticker} >>> {strategy} >>> {self.strategies[strategy]}")

        change_flag = True
        while change_flag:
            change_item = string_parser(
                self.ticker, "strategy ",
                ["name", "price", "quantity", "wp buy", "wp sell", "quit"])

            if change_item == "name":
                self.change_a_name_of_the_strategy(strategy)

            elif change_item == "price" or change_item == "p":
                price, _ = self.change_a_purchase_navigation(strategy)
                self.change_a_price_of_the_strategy(strategy, price)
                self.calculating_worth_and_quantity_of_the_asset()

            elif change_item == "quantity" or change_item == "q":
                price, quantity = self.change_a_purchase_navigation(strategy)
                self.change_a_quantity_of_the_strategy(strategy, price, quantity)
                self.calculating_worth_and_quantity_of_the_asset()

            elif change_item == "wp buy":
                self.change_wish_prices(strategy, "WP buy")

            elif change_item == "wp sell":
                self.change_wish_prices(strategy, "WP sell")

            elif change_item == "quit" or change_item == "exit":
                change_flag = False

            else:
                print(f"{change_item} command doesn't exist.")

    def change_a_name_of_the_strategy(self, strategy):
        new_name = input(f"{self.ticker} >>> {strategy} >>> Print a new name: ")
        self.strategies[new_name] = self.strategies[strategy]
        del self.strategies[strategy]

    def change_a_purchase_navigation(self, strategy):
        print(f"\n{strategy} >>> purchases: \n" + "\n".join(
            f"{price} : {quantity}" for price, quantity
            in self.strategies[strategy]["Purchases"].items()) + "\n")

        price = string_parser(
            self.ticker, "purchases >>> price ",
            self.strategies[strategy]["Purchases"].keys())

        return price, self.strategies[strategy]["Purchases"][price]

    def change_a_price_of_the_strategy(self, strategy, price):
        new_price = str(checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> {price} >>> "
                  f"Print a new price: "), message=self.ticker))

        self.strategies[strategy]["Purchases"][new_price] = \
            self.strategies[strategy]["Purchases"][price]

        del self.strategies[strategy]["Purchases"][price]
        print(f"\n{self.ticker} >>> {strategy} >>> {self.strategies[strategy]}\n")

    def change_a_quantity_of_the_strategy(self, strategy, price, quantity):
        self.strategies[strategy]["Purchases"][price] = \
            checking_if_an_input_is_a_number(
                input(f"{self.ticker} >>> {strategy} >>> {quantity} >>> "
                      f"Print a new quantity: "), message=self.ticker)
        print(f"\n{self.ticker} >>> {strategy} >>> {self.strategies[strategy]}\n")

    def change_wish_prices(self, strategy, price):
        print(f"{self.ticker} >>> {strategy} >>> {price} "
              f"= {self.strategies[strategy][price]} {self.currency}")
        self.strategies[strategy][price] = checking_if_an_input_is_a_number(
            input(f"{self.ticker} >>> {strategy} >>> {price} >>> Print a "
                  f"new {price}: "), message=self.ticker)
        print(f"{price} = {self.strategies[strategy][price]} {self.currency}\n")


def checking_if_an_input_is_a_number(value, message=None):
    while True:
        try:
            return float(value)
        except ValueError:
            value = input(f"{message} >>> You need to input a number. Please, try "
                          f"again: " if message else "You need to input a number. "
                                                     "Please, try again: ")


def string_parser(ticker, message, array_of_names):
    item = input(
        f"{ticker} >>> " + message + "[" +
        ", ".join(str(a) for a in array_of_names) + "]: ").lower()

    while True:
        if item in array_of_names:
            return item
        item = input(
            f"'{item}' is not in [" + ", ".join(a for a in array_of_names) +
            "]. Please, try again: ").lower()


def year_month_day_for_graph_builder():
    t1_array, t2_array, start_flag, finish_flag = [], [], True, True
    start_data, finish_data = None, None

    while start_flag:
        start_data = list(input("Start [Y M D]: ").split(" "))

        if len(start_data) < 3:
            print(f"There is a mistake: {start_data} -> [Y M D]")
        else:
            start_flag = False

    for number, checker in ((0, "Y"), (1, "M"), (2, "D")):
        t1_array.append(int(checking_if_an_input_is_a_number(
            start_data[number], checker)))

    start = dt.datetime(t1_array[0], t1_array[1], t1_array[2])

    while finish_flag:
        finish_data = input("Finish [Y M D] or 'now': ").lower()

        if finish_data == "now":
            return start, dt.datetime.now()
        elif len(finish_data) < 3:
            print(f"There is a mistake: {finish_data} -> [Y M D]")
        else:
            finish_flag = False

    finish_data = list(finish_data.split(" "))
    for number, checker in ((0, "Y"), (1, "M"), (2, "D")):
        t2_array.append(int(checking_if_an_input_is_a_number(
            finish_data[number], checker)))

    return start, dt.datetime(t2_array[0], t2_array[1], t2_array[2])


def a_small_navigation_after_some_functions(x, y, z):
    while True:
        print(f"\nIf you want to {x}, print '{y}' (any register).")
        print(f"If you want to finish, print '{z}' (any register).")

        navigation = input("Your command: ").lower()
        if navigation == y:
            return True
        elif navigation == z:
            return False
        else:
            print(f"The command: '{navigation}' is not define. Please, try again.")


def showing_on_the_display_all_information_for_the_start_of_the_program():
    global self_portfolio, other_portfolio, watchlist

    print("Financial monitoring. Version 1.2")
    print(f"Loading data ...")

    for v1, v2 in ((self_portfolio, "self_portfolio.json"),
                   (other_portfolio, "other_portfolio.json"),
                   (watchlist, "watchlist.json")):
        try:
            v1.loading_assets_data_from_json_file_to_the_bank_array(v2)
        except JsonDE:
            print(f"File: '{v2}' is empty. The '{v1.name}' has no assets.")
        else:
            if len(v1) == 0:
                print(f"Loading was finished, but the '{v1.name}' is still empty.")
            else:
                print(f"Loading was finished. There are {v1}.")

    print("-" * 107)
    for v3 in (self_portfolio, other_portfolio, watchlist):
        v3.sending_news_about_messages_to_the_display()


def a_small_menu_before_picking_any_function():
    print("-" * 107 + "\n\n" + ">>>  Main menu mode  <<<", end="\n\n")
    print("If you need any help, print 'help'.")
    print("If you want to exit the program, print 'exit'.")


def asking_about_exit_the_program_with_or_without_saving_data():
    global self_portfolio, other_portfolio, watchlist

    leaving_the_program_flag = True
    while leaving_the_program_flag:
        leaving = input("Do you want to exit the program? [yes, no]: ").lower()

        if leaving == "yes" or leaving == "y":
            leaving_the_program_flag = False
        elif leaving == "no" or leaving == "n":
            return True
        else:
            print(f"The command: '{leaving}' doesn't exist. Please, try again.")

    saving_data_flag = True
    while saving_data_flag:
        saving = input("Before leaving, do you want to save your data?"
                       " [yes, no]: ").lower()

        if saving == "yes" or saving == "y":
            for v1, v2 in ((self_portfolio, "self_portfolio.json"),
                           (other_portfolio, "other_portfolio.json"),
                           (watchlist, "watchlist.json")):
                v1.saving_information_from_the_bank_array_to_json_file(v2)
            saving_data_flag = False
        elif saving == "no" or saving == "n":
            saving_data_flag = False
        else:
            print(f"The command: '{saving}' doesn't exist. Please, try again.")

    print("That's all. Thank you for using our program.")
    return False


def help_me_function():
    print(">>>     Help     <<<")
    help_me_table = PtT(padding_width=2)
    help_me_table.field_names = ["Command", "Description"]
    help_me_table.add_row([
        "help", "Showing all available functions: [command - description]"])
    help_me_table.add_row(["-" * 30, "-" * 60])
    help_me_table.add_row(["portfolio", "Opening the portfolio mode"])
    help_me_table.add_row(["portfolio >>> self", "Portfolio (Self) Mode"])
    help_me_table.add_row(["portfolio >>> self", "Portfolio (Other) Mode"])
    help_me_table.add_row(["portfolio >>> show", "Show the portfolio (table)"])
    help_me_table.add_row(["portfolio >>> add", "Add a new asset in the portfolio"])
    help_me_table.add_row([
        "portfolio >>> delete", "Delete the asset from the portfolio"])
    help_me_table.add_row(["portfolio >>> change", "Change the value of the asset"])
    help_me_table.add_row(["portfolio >>> visual", "Visualisation of the portfolio"])
    help_me_table.add_row(["-" * 30, "-" * 60])
    help_me_table.add_row(["watchlist", "Opening the watchlist mode"])
    help_me_table.add_row(["watchlist >>> show", "Show the watchlist (table)"])
    help_me_table.add_row(["watchlist >>> add", "Add a new asset in the watchlist"])
    help_me_table.add_row([
        "watchlist >>> delete", "Delete the asset from the watchlist"])
    help_me_table.add_row(["watchlist >>> change", "Change the value of the asset"])
    help_me_table.add_row(["-" * 30, "-" * 60])
    help_me_table.add_row(["graph", "Building a graph"])
    help_me_table.add_row(["graph >>> one", "Put a ticker and make a graph"])
    help_me_table.add_row([
        "graph >>> multi", "Put a (*args) of tickers and make a graph"])
    help_me_table.add_row([
        "graph >>> heat", "Put a (*args) of tickers and make a heat map"])
    help_me_table.add_row(["-" * 30, "-" * 60])
    help_me_table.add_row(["exit", "Quit the program"])

    print(help_me_table, end='\n\n')


def a_small_menu_before_picking_any_function_in_some_mode(place, commands):
    """ ("Portfolio (Self)", "[show, add, delete, change, visual, help, quit]"),
        ("Portfolio (Other)", "[show, add, delete, change, visual, help, quit]"),
        ("Watchlist", "[show, add, delete, change, help, quit]"),
        ("Graph", "[one, multi, heat, help, quit]") """
    print("-" * 107 + "\n\n" + f">>>  {place} Mode  <<<", end="\n\n")
    print(f"What do you wish to do: {commands}.")


def building_a_graph_for_only_one_asset():
    global self_portfolio, other_portfolio, watchlist

    ticker = input("What is a ticker of an asset: ").upper()
    type_of_an_asset = None
    for array in (self_portfolio.bank, other_portfolio.bank, watchlist.bank):
        for asset in array:
            if ticker == asset.ticker:
                type_of_an_asset = asset.asset_type

    type_of_an_asset = type_of_an_asset or string_parser(
        ticker, "What is a type of an asset: ", ["stock", "crypto", "bond"])

    if type_of_an_asset == "crypto":
        ticker = f"{ticker}-USD"

    type_of_lines = string_parser(ticker, "What is a type of lines: ",
                                  ["candle", "line"])

    start, finish = year_month_day_for_graph_builder()
    volume = string_parser(ticker, "Do you need to see a volume chart? ",
                           ["yes", "no"])

    putting_a_ticker_get_a_graph(ticker, start, finish, type_of_lines, volume)


def putting_a_ticker_get_a_graph(ticker, start, finish, type_of_lines, volume):
    name = "night" + "clouds"
    colors = mpf.make_marketcolors(up="#00FF00", down="#FF0000",
                                   wick="inherit", edge="inherit")
    mpf_style = mpf.make_mpf_style(base_mpf_style=name, marketcolors=colors)

    if volume == "yes" or volume == "y":
        mpf.plot(web.DataReader(ticker, "yahoo", start, finish),
                 type=type_of_lines, style=mpf_style, volume=True, title=f'{ticker}')
    elif volume == "no" or volume == "n":
        mpf.plot(web.DataReader(ticker, "yahoo", start, finish),
                 type=type_of_lines, style=mpf_style, title=f'{ticker}')


def a_small_visualisation_of_the_portfolio():
    global self_portfolio, other_portfolio

    if string_parser("Portfolio", "visual ", ["self", "other"]) == "self":
        title = "Self Portfolio"
        tickers = [asset.ticker for asset in self_portfolio.bank]
        total = [round((asset.quantity * asset.price), 2)
                 for asset in self_portfolio.bank]
        bought = [asset.worth_of_all for asset in self_portfolio.bank]
        line = self_portfolio.bank
    else:
        title = "Other Portfolio"
        tickers = [asset.ticker for asset in other_portfolio.bank]
        total = [round((asset.quantity * asset.price), 2)
                 for asset in other_portfolio.bank]
        bought = [asset.worth_of_all for asset in other_portfolio.bank]
        line = other_portfolio.bank

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor("black")
    ax.figure.set_facecolor("#121212")
    ax.tick_params(axis="x", color="white")
    ax.tick_params(axis="y", color="white")
    ax.set_title("Portfolio", color="white", fontsize=20)

    _, texts, _ = ax.pie(total, labels=tickers, autopct="%1.1f%%", pctdistance=0.8)
    [text.set_color("white") for text in texts]
    plt.gca().add_artist(plt.Circle((0, 0), 0.55, color="black"))

    ax.text(-2, 1, title, fontsize=14, color="white",
            verticalalignment="center", horizontalalignment="center")
    ax.text(-2, 0.65, f"Total worth: {sum(total)}", fontsize=12, color="white",
            verticalalignment="center", horizontalalignment="center")

    counter = 0.15
    for ticker, ttl in zip(tickers, total):
        for asset in line:
            if ticker == asset.ticker:
                ax.text(-2, 0.45 - counter, f"{ticker}: {ttl} {asset.currency}",
                        fontsize=12, color="white", verticalalignment="center",
                        horizontalalignment="center")
        counter += 0.15

    delta_overall = round((sum(total) - sum(bought)), 2)
    ax.text(2, 1, "Delta", fontsize=14, color="white",
            verticalalignment="center", horizontalalignment="center")
    ax.text(2, 0.65, f"Total delta: {delta_overall}", fontsize=12,
            color="green" if delta_overall >= 0 else "red",
            verticalalignment="center", horizontalalignment="center")

    counter = 0.15
    for ticker, asset_buy, asset_now in zip(tickers, bought, total):
        for asset in line:
            if ticker == asset.ticker:
                delta_asset = round((asset_now - asset_buy), 2)
                ax.text(2, 0.45 - counter, f"{ticker}: {delta_asset} {asset.currency}",
                        fontsize=12, color="green" if delta_asset >= 0 else "red",
                        verticalalignment="center", horizontalalignment="center")
        counter += 0.15

    plt.show()


def making_a_graph_for_more_than_two_companies():
    global self_portfolio, other_portfolio, watchlist

    tickers_list = returning_an_array_of_tickers_for_building_graphs_and_maps(
        "Graph >>> multi")
    data = pnd.DataFrame(columns=tickers_list)
    start, finish = year_month_day_for_graph_builder()

    for ticker in tickers_list:
        data[ticker] = yf.download(ticker, start, finish)["Adj Close"]

    chart_line_flag = True
    while chart_line_flag:
        print("Choose a type of a chart: [absolute, percent]: ")
        chart_line = input("Graph >>> multi >>> chart >>> ").lower()
        if chart_line == "absolute" or chart_line == "abs" or chart_line == "a":
            data.plot(figsize=(12, 6))
            chart_line_flag = False
        elif chart_line == "percent" or chart_line == "per" or chart_line == "p":
            (data.pct_change() + 1).cumprod().plot(figsize=(12, 6))
            chart_line_flag = False
        else:
            print(f"The command: '{chart_line}' doesn't exist. Please, try again.")

    plt.legend()
    plt.title("Adjusted Close Price", fontsize=16)
    plt.ylabel("Price", fontsize=14)
    plt.xlabel("Year", fontsize=14)
    plt.grid(which="major", linestyle="-", linewidth=0.5)
    plt.show()


def returning_an_array_of_tickers_for_building_graphs_and_maps(message):
    multi_lines_flag, tickers_list = True, []
    print(f"{message} >>> print [any ticker, 'done', 'self_portfolio', "
          f"'other_portfolio', 'watchlist'].\nIf crypto => 'ticker-USD'")

    while multi_lines_flag:
        multi_lines_input = input("Graph >>> multi >>> ").upper()

        if multi_lines_input == "SELF_PORTFOLIO":
            tickers_list = appending_tickers_to_the_list(self_portfolio)
        elif multi_lines_input == "OTHER_PORTFOLIO":
            tickers_list = appending_tickers_to_the_list(other_portfolio)
        elif multi_lines_input == "WATCHLIST":
            tickers_list = appending_tickers_to_the_list(watchlist)
        elif multi_lines_input == "DONE":
            multi_lines_flag = False
        else:
            tickers_list.append(multi_lines_input)

    return tickers_list


def appending_tickers_to_the_list(place):
    tickers_list = []
    for asset in place.bank:
        if asset.asset_type in ("stock", "bond"):
            tickers_list.append(asset.ticker)
        elif asset.asset_type == "crypto":
            tickers_list.append(f"{asset.ticker}-{asset.currency}")
    return tickers_list


def making_a_heat_map():
    tickers_list = returning_an_array_of_tickers_for_building_graphs_and_maps("Heat")
    column_names, first_flag, combined_data = [], True, None
    start, finish = year_month_day_for_graph_builder()

    for ticker in tickers_list:
        data = web.DataReader(ticker, "yahoo", start, finish)

        if first_flag:
            combined_data = data[["Close"]].copy()
            column_names.append(ticker)
            combined_data.columns = column_names
            first_flag = False
        else:
            combined_data = combined_data.join(data["Close"])
            column_names.append(ticker)
            combined_data.columns = column_names

    sns.heatmap(combined_data.pct_change().corr(method="pearson"),
                annot=True, cmap="cool" + "warm")
    plt.show()


if __name__ == "__main__":
    # making all Bank() variables.
    self_portfolio = Bank("Portfolio (Self)")
    other_portfolio = Bank("Portfolio (Other)")
    watchlist = Bank("Watchlist")
    showing_on_the_display_all_information_for_the_start_of_the_program()

    main_menu_flag = True
    while main_menu_flag:
        a_small_menu_before_picking_any_function()
        text_input = input("Your command: ").lower()
        print(end="\n")

        if text_input == "help":
            help_me_function()

        elif text_input == "messages":
            print(">>>     Messages     <<<\n")
            for i001 in (self_portfolio, other_portfolio, watchlist):
                i001.sending_all_messages_to_the_display()

        elif text_input == "portfolio":
            ptp = string_parser("Portfolio", "Pick a portfolio ", ["self", "other"])
            portfolio = self_portfolio if ptp == "self" else other_portfolio
            mim = "Self" if ptp == "self" else "Other"

            portfolio_flag = True
            while portfolio_flag:
                a_small_menu_before_picking_any_function_in_some_mode(
                    f"{mim} Portfolio",
                    "[show, add, delete, change, visual, help, quit]")
                the_portfolio_mode_input = input("Your command: ").lower()

                if the_portfolio_mode_input == "help":
                    help_me_function()

                elif the_portfolio_mode_input == "show":
                    portfolio.showing_the_bank_on_the_display()

                elif the_portfolio_mode_input == "add":
                    portfolio.adding_a_new_asset_or_a_new_strategy()

                elif the_portfolio_mode_input == "delete":
                    portfolio.deleting_the_asset_from_the_bank()

                elif the_portfolio_mode_input == "change":
                    portfolio.a_function_for_changing_something_inside_the_asset()

                elif the_portfolio_mode_input == "visual":
                    a_small_visualisation_of_the_portfolio()

                elif the_portfolio_mode_input == "exit" or \
                        the_portfolio_mode_input == "quit":
                    portfolio_flag = False
                    continue

                else:
                    print(f"The command: '{the_portfolio_mode_input}' doesn't exist. "
                          f"Please, try again.")

        elif text_input == "watchlist":
            watchlist_flag = True
            while watchlist_flag:
                a_small_menu_before_picking_any_function_in_some_mode(
                    "Watchlist", "[show, add, delete, change, help, quit]")
                the_watchlist_mode_input = input("Your command: ").lower()

                if the_watchlist_mode_input == "help":
                    help_me_function()

                elif the_watchlist_mode_input == "show":
                    watchlist.showing_the_bank_on_the_display()

                elif the_watchlist_mode_input == "add":
                    watchlist.adding_a_new_asset_or_a_new_strategy()

                elif the_watchlist_mode_input == "delete":
                    watchlist.deleting_the_asset_from_the_bank()

                elif the_watchlist_mode_input == "change":
                    watchlist.a_function_for_changing_something_inside_the_asset()

                elif the_watchlist_mode_input == "exit" or \
                        the_watchlist_mode_input == "quit":
                    watchlist_flag = False
                    continue

                else:
                    print(f"The command: '{the_watchlist_mode_input}' doesn't exist. "
                          f"Please, try again.")

        elif text_input == "graph":
            graph_flag = True
            while graph_flag:
                a_small_menu_before_picking_any_function_in_some_mode(
                    "Graph", "[one, multi, heat, help, quit]")
                the_graph_mode_input = input("Your command: ").lower()

                if the_graph_mode_input == "help":
                    help_me_function()

                elif the_graph_mode_input == "one":
                    building_a_graph_for_only_one_asset()

                elif the_graph_mode_input == "multi":
                    making_a_graph_for_more_than_two_companies()

                elif the_graph_mode_input == "heat":
                    making_a_heat_map()

                elif the_graph_mode_input == "exit" or \
                        the_graph_mode_input == "quit":
                    graph_flag = False
                    continue

                else:
                    print(f"The command: '{the_graph_mode_input}' doesn't exist. "
                          f"Please, try again.")

        elif text_input == "exit":
            main_menu_flag = asking_about_exit_the_program_with_or_without_saving_data()

        else:
            print(f"The command: '{text_input}' doesn't exist. Please, try again.")
