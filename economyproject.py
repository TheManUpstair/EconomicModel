class FirmType:
    def __init__(self, name, level, input_goods, input_amounts, output_goods, output_amounts):
        self.name = name
        self.level = level
        self.input_goods = input_goods
        self.input_amounts = input_amounts
        self.output_goods = output_goods
        self.output_amounts = output_amounts

class FirmHandler:
    def __init__(self):
        self.all_firms = [[], [], []]
    
    def new_firm(self, firm_type, cash):
        self.all_firms[firm_type.level].append(Firm(firm_type, cash))

class Firm:
        def __init__(self, firm_type, cash):
            self.firm_type = firm_type
            self.cash = cash
            self.good_in_storage_amounts = [0] * len(self.firm_type.output_goods)
        
        def produce_goods(self):
            # Primary producer, takes in no input goods
            if self.firm_type.level == 0:
                for i in range(0, len(self.good_in_storage_amounts)):
                   self.good_in_storage_amounts[i] += self.firm_type.output_amounts[i]
            # Non-primary produce, takes in input goods
            else:
                # Buy input goods
                self.percent_of_inputs_aquired = [0] * len(self.firm_type.input_goods)
                for i in range(0, len(self.firm_type.input_goods)):
                    for firm_to_buy_from in firm_handler.all_firms[self.firm_type.level - 1]:
                        if self.cash > 0 and self.percent_of_inputs_aquired[i] < 1 and self.firm_type.input_goods[i] in firm_to_buy_from.firm_type.output_goods:
                            # Calculate the amount can buy
                            self.amount_bought = round(self.cash / self.firm_type.input_goods[i].price)
                            self.amount_bought = min(self.amount_bought, self.firm_type.input_amounts[i])
                            self.amount_bought = min(self.amount_bought, (1 - self.percent_of_inputs_aquired[i]) * self.firm_type.input_amounts[i])
                            # Actually buy the good
                            firm_to_buy_from.cash += self.amount_bought * self.firm_type.input_goods[i].price
                            self.cash -= self.amount_bought * self.firm_type.input_goods[i].price
                            self.percent_of_inputs_aquired[i] += self.amount_bought / self.firm_type.input_amounts[i]
                # Produce output goods
                self.percentage_to_produce = min(self.percent_of_inputs_aquired)
                for i in range(0, len(self.firm_type.output_goods)):
                    self.good_in_storage_amounts[i] += self.firm_type.output_amounts[i] * self.percentage_to_produce

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

class Good:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.demand = 0
    
    def calculate_demand(self, list_of_purchasers):
        self.demand = 0
        for purchaser in list_of_purchasers:
            self.demand += 1

# Define goods
good_handler = GoodHandler()
good_handler.new_good("Timber", 1)
good_handler.new_good("Wooden Planks", 1.5)

# Define firm types
TimberLogging = FirmType("Timber Logging", 0, [], [], [good_handler.get_good("Timber")], [1])
Sawmill = FirmType("Sawmill", 1, [good_handler.get_good("Timber")], [1], [good_handler.get_good("Wooden Planks")] , [1])

# Define firms
firm_handler = FirmHandler()
firm_handler.new_firm(TimberLogging, 10)
firm_handler.new_firm(Sawmill, 10)

# Wipe debug file
open('output.txt', 'w').close()

# Do daily cycle
days_left = 100
while days_left > 0:
    # Primary level firms produce goods
    for firm in firm_handler.all_firms[0]:
        firm.produce_goods()
    # Second level firms buy goods
    for firm in firm_handler.all_firms[1]:
        firm.produce_goods()
    # Print output - total money in the economy
    total_money_in_world = sum(firm.cash for firm_level in firm_handler.all_firms for firm in firm_level)
    with open('output.txt', 'a') as outputtxt:
        outputtxt.write(str(total_money_in_world) + '\n')
    days_left -= 1

# Make debug graph
import matplotlib.pyplot as plt
data, days, day = [], [], 1
with open('output.txt', 'r') as f:
    for line in f:
        data.append(float(line))
        days.append(day)
        day += 1
plt.scatter(days, data)