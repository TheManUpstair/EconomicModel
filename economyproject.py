from math import floor # Used for purchasing goods

# FirmType respresents what industry a firm is in. For example, a sawmill (takes in timber and produces wooden planks).
class FirmType:
    def __init__(self, name, level, input_goods, input_amounts, output_good, output_amount):
        self.name = name
        self.level = level
        self.input_goods = input_goods
        self.input_amounts = input_amounts
        self.output_good = output_good
        self.output_amount = output_amount

# The Firm Handler just handles the list of all firms. The all_firms list is split up by the tier of industry the firm is in. For example, primary industries are in the first list, secondary industries in the second, and so on.
class FirmHandler:
    def __init__(self):
        self.all_firms = [[], [], []]
        self.number_of_firms = 0
    
    def new_firm(self, firm_type, cash, size):
        self.all_firms[firm_type.level].append(Firm(firm_type, cash, size))
        self.number_of_firms += 1
    
    def calculate_total_hiring_capacity(self):
        self.total_firm_sizes = 0
        for firm_level in self.all_firms:
            for firm in firm_level:
                self.total_firm_sizes += firm.maximum_size

# The firm class represents each individual factory or firm. It handles all of the day-by-day functions of a firm, for example, producing goods.
class Firm:
    def __init__(self, firm_type, cash, size):
        self.firm_type = firm_type
        self.cash = cash
        self.maximum_size = size
        self.sold_last_year = -1
        self.good_in_storage = 0
    
    def produce_goods(self):
        # Get the effective size of the factory, currently equal to worker numbers
        self.get_effective_size()
        # Primary producer, takes in no input goods
        if self.firm_type.level == 0:
            self.good_in_storage += self.firm_type.output_amount * self.effective_size * 100
            self.firm_type.output_good.amount_produced += self.firm_type.output_amount * self.effective_size * 100
            print(self.firm_type.name, "produced", self.firm_type.output_amount * self.effective_size * 100, self.firm_type.output_good.name)
        # Non-primary producer, takes in input goods
        else:
            # Buy input goods
            self.percent_of_inputs_aquired = [0] * len(self.firm_type.input_goods)
            if self.sold_last_year > 0:
                self.desired_output = self.sold_last_year * 1.1
            elif self.sold_last_year == -1:
                self.desired_output = self.effective_size * 100
            elif self.sold_last_year == 0:
                self.desired_output = 10
            else:
                raise Exception("Buying input goods produced last year messing up")
            # if self.good_in_storage > 1000:
            #     self.desired_output = 10
            for i in range(0, len(self.firm_type.input_goods)):
                for firm_to_buy_from in firm_handler.all_firms[self.firm_type.level - 1]:
                    if self.cash > 0 and self.percent_of_inputs_aquired[i] < 1 and self.firm_type.input_goods[i] == firm_to_buy_from.firm_type.output_good:
                        # Calculate the amount to buy
                        self.amount_bought = floor(min(self.cash / self.firm_type.input_goods[i].price, (1 - self.percent_of_inputs_aquired[i]) * self.firm_type.input_amounts[i] * self.desired_output, firm_to_buy_from.good_in_storage))
                        # Actually buy the good
                        firm_to_buy_from.cash += self.amount_bought * self.firm_type.input_goods[i].price
                        firm_to_buy_from.good_in_storage -= self.amount_bought
                        firm_to_buy_from.sold_last_year += self.amount_bought
                        self.cash -= self.amount_bought * self.firm_type.input_goods[i].price
                        self.percent_of_inputs_aquired[i] += self.amount_bought / (self.firm_type.input_amounts[i] * self.desired_output)
                        self.firm_type.input_goods[i].amount_sold += self.amount_bought
                        print(self.firm_type.name, "bought", self.amount_bought, "for", self.amount_bought * self.firm_type.input_goods[i].price)
            self.produce_output_good()
            
    
    def produce_output_good(self):
        self.percentage_to_produce = min(self.percent_of_inputs_aquired)
        self.amount_produced = self.firm_type.output_amount * self.percentage_to_produce * self.desired_output
        self.good_in_storage += self.amount_produced
        self.firm_type.output_good.amount_produced += self.amount_produced
        print(self.firm_type.name, "produced", self.amount_produced, self.firm_type.output_good.name, "desired", self.desired_output)
                
    def decide_to_expand_firm(self):
        # If a firm has $25000 in reserve and no unused goods, then it'll expand for $10k
        if self.cash > 25000 and self.good_in_storage == 0:
            self.cash -= 10000
            people.cash += 10000 # The extra cash goes to 'the economy' to be recycled
            self.maximum_size += 1
        # If a firm has a ton of goods in reserve it can shrink
        elif self.maximum_size > 1 and people.cash > 15000 and self.good_in_storage > 1000:
            self.cash += 7500
            people.cash -= 7500
            self.maximum_size -= 1
    
    # Distributes workers. Currently assumed that all jobs are equally desired.
    def get_effective_size(self):
        self.effective_size = floor(min(self.maximum_size, people.size * self.maximum_size / firm_handler.total_firm_sizes))
        
# The good handler handles all of the goods present.
class GoodHandler:
    def __init__(self):
        self.all_goods = []
    
    def new_good(self, name, price):
        self.all_goods.append(Good(name, price))
        
    def get_good(self, name):
        for good in self.all_goods:
            if good.name == name:
                return good
        raise Exception("Good not found in get_good")

# The good class represents each individual good. It handles pricing information.
class Good:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.base_price = price
        self.reset_daily_stats()
        
    def reset_daily_stats(self):
        self.amount_produced = 0
        self.amount_sold = 0
        
    def calculate_potential_demand(self):
        self.potential_demand = 0
        for firm_level in firm_handler.all_firms:
            for firm in firm_level:
                if self in firm.firm_type.input_goods:
                    self.potential_demand += firm.firm_type.input_amounts[firm.firm_type.input_goods.index(self)] * firm.effective_size * 100
    
    def update_price(self):
        self.calculate_potential_demand()
        if self.amount_produced > self.amount_sold:
            self.price -= 0.1
        elif self.amount_produced < self.amount_sold:
            self.price += 0.1
        if self.price < 0.1:
            self.price = 0.1
        self.price = round(self.price, 1)

# The population class represents the general population.
class Population:
    def __init__(self, size, cash):
        self.size = size
        self.cash = cash
                
# Define goods
good_handler = GoodHandler()
good_handler.new_good("Timber", 1)
good_handler.new_good("Wooden Planks", 2)
good_handler.new_good("Furniture", 8)
# good_handler.new_good("Intruments", 16)

# Define firm types
TimberLogging = FirmType("Timber Logging", 0, [], [], good_handler.get_good("Timber"), 1)
Sawmill = FirmType("Sawmill", 1, [good_handler.get_good("Timber")], [1], good_handler.get_good("Wooden Planks") , 1)
FurnitureFactory = FirmType("Furniture", 2, [good_handler.get_good("Wooden Planks")], [2], good_handler.get_good("Furniture") , 1)
# InstrumentFactory = FirmType("Intruments", 2, [good_handler.get_good("Wooden Planks")], [4], [good_handler.get_good("Intruments")] , [1])

# Define firms
firm_handler = FirmHandler()
firm_handler.new_firm(TimberLogging, 0, 10)
firm_handler.new_firm(Sawmill, 10000, 10)
firm_handler.new_firm(FurnitureFactory, 10000, 5)

# Define population
people = Population(10000, 20000)

# Wipe debug file
open('output.txt', 'w').close()

# Do daily cycle
days_left = 3650
while days_left > 0:
    # Prepare firm checkbooks
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            firm.last_year_profit = 0
            firm.starting_cash = firm.cash
            firm.sold_last_year = 0
            
    # Prepare good balances
    for good in good_handler.all_goods:
        good.reset_daily_stats()
            
    # Firms produce goods
    firm_handler.calculate_total_hiring_capacity()
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            firm.produce_goods()
    
    # Have the people buy all third-level outputs
    for firm in firm_handler.all_firms[2]:
        amount_to_buy = floor(min(people.cash / firm.firm_type.output_good.price, firm.good_in_storage)) # assuming infinite demand outside of price
        firm.good_in_storage -= amount_to_buy
        firm.cash += amount_to_buy * firm.firm_type.output_good.price
        firm.sold_last_year += amount_to_buy
        people.cash -= amount_to_buy * firm.firm_type.output_good.price
        print("The people bought", amount_to_buy, firm.firm_type.name, "for", amount_to_buy * firm.firm_type.output_good.price)
            
    # Firms pay their works half of profits
    # Prepare firm checkbooks
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            # Then split the profits, with 50% going to shareholders / employees and 50% being retained for tomorrow's operations. Primary producers keep 100%, for now.
            firm.profit = firm.cash - firm.starting_cash
            if firm.firm_type.level == 0:
                people.cash += firm.cash
                firm.cash = 0
            # else:
                if firm.profit > 0:
                    firm.cash -= floor(firm.profit * 5 / 10)
                    people.cash += floor(firm.profit * 5 / 10)
    
    # Firms decide whether to expand or contract
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            firm.decide_to_expand_firm()
    
    # Adjust good prices
    for good in good_handler.all_goods:
        good.update_price()
    
    # Get debug output, useful for graphing to see if money / goods are magically appearing (read: my min statement spaghetti blew up)
    print()
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            print(firm.firm_type.name, firm.maximum_size, "$" + str(round(firm.cash)), firm.good_in_storage, firm.sold_last_year)
    print("People", "$" + str(people.cash))
    for good in good_handler.all_goods:
        print(good.name, good.amount_produced, good.amount_sold, good.price)
    total_money_in_world = sum(firm.cash for firm_level in firm_handler.all_firms for firm in firm_level) + people.cash
    with open('output.txt', 'a') as outputtxt:
        # outputtxt.write(str(total_money_in_world) + '\n')
        # outputtxt.write(str(firm_handler.all_firms[1][0].cash) + '\n')
        outputtxt.write(str(people.cash) + '\n')
    
    # Iterate to the next day
    days_left -= 1

# Make debug graph
import matplotlib.pyplot as plt
data, days, day = [], [], 1
with open('output.txt', 'r') as f:
    for line in f:
        data.append(float(line))
        days.append(day/365)
        day += 1
plt.scatter(days, data)
