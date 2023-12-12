from math import floor # Used for purchasing goods

# FirmType respresents what industry a firm is in. For example, a sawmill (takes in timber and produces wooden planks).
class FirmType:
    def __init__(self, name, level, input_goods, input_amounts, output_goods, output_amounts):
        self.name = name
        self.level = level
        self.input_goods = input_goods
        self.input_amounts = input_amounts
        self.output_goods = output_goods
        self.output_amounts = output_amounts

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
        self.good_in_storage_amounts = [0] * len(self.firm_type.output_goods)
    
    def produce_goods(self):
        # Get the effective size of the factory, currently equal to worker numbers
        self.get_effective_size()
        # Primary producer, takes in no input goods
        if self.firm_type.level == 0:
            for i in range(0, len(self.good_in_storage_amounts)):
               self.good_in_storage_amounts[i] += self.firm_type.output_amounts[i] * self.effective_size * 1000
        # Non-primary produce, takes in input goods
        else:
            # Buy input goods
            self.percent_of_inputs_aquired = [0] * len(self.firm_type.input_goods)
            for i in range(0, len(self.firm_type.input_goods)):
                for firm_to_buy_from in firm_handler.all_firms[self.firm_type.level - 1]:
                    if self.cash > 0 and self.percent_of_inputs_aquired[i] < 1 and self.firm_type.input_goods[i] in firm_to_buy_from.firm_type.output_goods:
                        # Calculate the amount to buy
                        self.amount_bought = floor(min(self.cash / self.firm_type.input_goods[i].price, self.firm_type.input_amounts[i] * self.effective_size * 1000, (1 - self.percent_of_inputs_aquired[i]) * self.firm_type.input_amounts[i] * self.effective_size * 1000, firm_to_buy_from.good_in_storage_amounts[firm_to_buy_from.firm_type.output_goods.index(self.firm_type.input_goods[i])]))
                        # Actually buy the good
                        firm_to_buy_from.cash += self.amount_bought * self.firm_type.input_goods[i].price
                        firm_to_buy_from.good_in_storage_amounts[firm_to_buy_from.firm_type.output_goods.index(self.firm_type.input_goods[i])] -= self.amount_bought
                        self.cash -= self.amount_bought * self.firm_type.input_goods[i].price
                        self.percent_of_inputs_aquired[i] += self.amount_bought / (self.firm_type.input_amounts[i] * self.effective_size * 1000)
            # Produce output goods
            self.percentage_to_produce = min(self.percent_of_inputs_aquired)
            for i in range(0, len(self.firm_type.output_goods)):
                self.good_in_storage_amounts[i] += self.firm_type.output_amounts[i] * self.percentage_to_produce * self.effective_size * 1000
                
    def decide_to_expand_firm(self):
        # If a firm has $25000 in reserve and no unused goods, then it'll expand for $10k
        if self.cash > 25000 and min(self.good_in_storage_amounts) == 0:
            self.cash -= 10000
            self.maximum_size += 1
    
    # Distributes workers. Currently assumed that all jobs are equally desired.
    def get_effective_size(self):
        self.effective_size = floor(min(self.maximum_size, total_population * self.maximum_size / firm_handler.total_firm_sizes))
        
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
    
    def update_price(self):
        self.leftover = 0
        for firm_level in firm_handler.all_firms:
            for firm in firm_level:
                if self in  firm.firm_type.output_goods:
                    self.leftover += firm.good_in_storage_amounts[firm.firm_type.output_goods.index(self)]
                
# Define goods
good_handler = GoodHandler()
good_handler.new_good("Timber", 1)
good_handler.new_good("Wooden Planks", 1.5)
good_handler.new_good("Furniture", 6)

# Define firm types
TimberLogging = FirmType("Timber Logging", 0, [], [], [good_handler.get_good("Timber")], [1])
Sawmill = FirmType("Sawmill", 1, [good_handler.get_good("Timber")], [1], [good_handler.get_good("Wooden Planks")] , [1])
FurnitureFactory = FirmType("Furniture", 2, [good_handler.get_good("Wooden Planks")], [3], [good_handler.get_good("Furniture")] , [1])

# Define firms
firm_handler = FirmHandler()
firm_handler.new_firm(TimberLogging, 1000, 1)
firm_handler.new_firm(Sawmill, 1000, 1)
firm_handler.new_firm(FurnitureFactory, 1000, 1)

# Limit labor growth
total_population = 10000

# Wipe debug file
open('output.txt', 'w').close()

# Do daily cycle
days_left = 365
while days_left > 0:
    # Firms produce goods
    print()
    firm_handler.calculate_total_hiring_capacity()
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            firm.produce_goods()
            print(firm.firm_type.name, firm.effective_size, firm.good_in_storage_amounts)
    
    # Have imaginary pops buy all third-level outputs -- assuming population = demand
    for firm in firm_handler.all_firms[2]:
        for i in range(0, len(firm.firm_type.output_goods)):
            amount_to_buy = min(firm.good_in_storage_amounts[i], total_population)
            firm.cash += amount_to_buy * firm.firm_type.output_goods[i].price
            firm.good_in_storage_amounts[i] -= amount_to_buy
    
    # Firms decide whether to expand or contract
    for firm_level in firm_handler.all_firms:
        for firm in firm_level:
            firm.decide_to_expand_firm()
    
    # Adjust good prices
    for good in good_handler.all_goods:
        good.update_price()
    
    # Get debug output, useful for graphing to see if money / goods are magically appearing (read: my min statement spaghetti blew up)
    total_money_in_world = sum(firm.cash for firm_level in firm_handler.all_firms for firm in firm_level)
    with open('output.txt', 'a') as outputtxt:
        outputtxt.write(str(total_money_in_world) + '\n')
    
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
