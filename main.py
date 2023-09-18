import statistics
import pathlib
import csv
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np

ACCEPTED_DELTA_DAYS = timedelta(days=3)

class Customer:
    def __init__(self, name, phone):
        # treat phone as primary key 
        self.name = name
        self.phone = phone
        self.leads = []

    def printInfo(self):
        print(f'Name: {self.name}')
        i = 0
        for lead in self.leads:
            i += 1
            print(f'Lead {i}: {lead.date}')
        pass

    def __eq__(self, other):
        return self.phone==other.phone\
            and self.name==other.name
    def __hash__(self) -> int:
        return hash(('phone', self.phone, 'name', self.name))


class Lead:

    format = "%y/%m/%d %H:%M:%S"

    def __init__(self, row):
        self.name = row[0]
        self.phone = row[1]
        self.zip = row[2]
        self.delivery = row[3]
        self.size = row[4]
        self.city = row[5]
        self.date =  datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')

    def printInfo(self):
        print(f'Name: {self.name}')
        print(f'Phone: {self.phone}')
        print(f'Zip: {self.zip}')
        print(f'Date: {self.date}')


def parse_web_data(filepath):
    with open(filepath, 'r', newline='') as csvfile:
        print(f'start parse of file: {filepath}')
        csvreader = csv.reader(csvfile)

        line_count = 0
        all_customers = []
        
        for row in csvreader:
            if line_count == 0:
                print(f'Col headers are {", ".join(row)}')
                line_count += 1
            else:
                create_lead(row, all_customers)
                line_count += 1

        print(f'total lines: {line_count}')

        duplicates = get_duplicate_array(all_customers)

        actual_multiple_submissions = parse_duplicates(duplicates)
    
        return duplicates, actual_multiple_submissions, (line_count - 1)

def create_lead(row, all_customers):
    # check for dupes
    if any(item.phone == row[1] for item in all_customers):
        # create new lead and add to existing customer
        # index = next((i for i, item in all_customers if item.phone == row[0]), -1)
        index = -1
        
        for i in range(len(all_customers)):
            if all_customers[i].phone == row[1]:
                index = i
                break
        
        # print("Dupe Found: ")
        # all_customers[index].printInfo()
        new_lead = Lead(row)
        all_customers[index].leads.append(new_lead)
        # print(f'Update: ')
        # all_customers[index].printInfo()

    else:
        # create new customer and add lead to customer
        new_customer = Customer(row[0], row[1])
        new_lead = Lead(row)
        new_customer.leads.append(new_lead)
        all_customers.append(new_customer)
    
def get_duplicate_array(all_customers):
    has_multiple_leads = []
    for i in range(len(all_customers)):
        if len(all_customers[i].leads) > 1:
            has_multiple_leads.append(all_customers[i])
    
    return has_multiple_leads

def parse_duplicates(customer_list):

    return_customers = []

    for i in range(len(customer_list)):
        current = customer_list[i]
        lead_list = current.leads

        # parse through list of leads, check to see if multiple subs exists
        lead_one_date = lead_list[0].date
        for z in range(len(lead_list)):
            if (lead_list[z].date - lead_one_date) > ACCEPTED_DELTA_DAYS:
                return_customers.append(current)

    return return_customers;

def parse_web_data_numpy(filepath):
    with open(filepath, 'r', newline='') as csvfile:
        print(f'start parse of file: {filepath}')
        csvreader = csv.reader(csvfile)

        line_count = 0
        source_arr = np.array([Customer])
        customers_list = []

        for row in csvreader:
            if line_count == 0:
                print("parsed headers (pass 1)")
                line_count += 1
            else:
               new_customer = Customer(row[0], row[1])
               customers_list.append(new_customer)
               line_count += 1

        print(f'Total Lines: {line_count}')
        customers_list = list(set(customers_list))

        customers = np.array(customers_list)

        print("Removed Duplicate Customers")

        # add leads to customer
        line_count = 0
        csvfile.seek(0)
        for row in csvreader:
            if line_count == 0:
                print("parsed headers (pass 2)")
                line_count += 1
            else:
               phone_no = row[1]
               new_lead = Lead(row)
               line_count += 1
               for customer in customers:
                   if customer.phone == phone_no:
                       customer.leads.append(new_lead)
                       break
        print("Leads added to Customer objects")           
        customers_with_multiple_leads = []
        for customer in customers:
            if len(customer.leads) > 1:
                customers_with_multiple_leads.append(customer)
        
        returning_customers = []
        for customer in customers_with_multiple_leads:
            lead_one_date = customer.leads[0].date
            for lead in customer.leads:
                if (lead.date - lead_one_date) > ACCEPTED_DELTA_DAYS:
                    returning_customers.append(customer)
                    break
        
        print("Parsed multiple lead customers")

        return customers_with_multiple_leads, returning_customers, line_count - 1



def plot_basic_stats(multiple_leads, returning_customers, total, title):
    
    # fig, ax = plt.subplots()

    # bottom_labels = ['Total Leads', 'Customers with Multiple Submissions', 'Returning Customers']
    # counts = [total, len(multiple_leads), len(returning_customers)]
    # bar_labels = ['red', 'blue', 'orange']
    # bar_colors = ['tab:red', 'tab:red', 'tab:red']

    # ax.bar(bottom_labels, counts, label=bar_labels, color=bar_colors)

    # ax.set_ylabel('Leads')
    # ax.set_title('Duplicate Lead Data')
    # ax.legend(title='Lead Data')

    x = np.array(["Total Leads", "Customers with\n Multiple Submissions", "Returning Customers"])
    
    y = np.array([total, len(multiple_leads), len(returning_customers)])

    plt.bar(x,y)
    plt.title(f'Data from: {title}')

    plt.show()
    



if __name__ == "__main__":
    
    # web_leads = parse_web_data("./data/all_web_leads.csv")
    # multiple_leads, returning_customers, total_leads = parse_web_data_numpy("./data/mini_test_data.csv")
    # multiple_leads, returning_customers, total_leads = parse_web_data_numpy("./data/all_web_leads.csv")
    # plot_basic_stats(multiple_leads, returning_customers, total_leads, title="Mini Test Data")

    multiple_leads, returning_customers, total_leads = parse_web_data("./data/all_web_leads.csv")
    plot_basic_stats(multiple_leads, returning_customers, total_leads, title="All_Web_Leads")
    
    
    



    


