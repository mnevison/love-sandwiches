import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint 

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')

def get_sales_data():
    """
    Get sales figures input from user
    """
    while True: 
        print("Please enter sales data from last market")
        print("Data should be six numbers, separated by commas")
        print("Example: 10, 20, 30, 40, 50, 60\n")

        data_str = input("Enter your data here: ")
        print(f"The data provided is {data_str}")

        sales_data = data_str.split(",")
        

        if validate_data(sales_data):
            print("Data is valid")
            break
    return sales_data

def validate_data(values):
    """
    inside the try, converts all string values into int
    raises value error if string cannot be converted into int
    or if there aren't exactly 6 values. 
    """
    
    try:
        [int(value) for value in values]
        if len(values) !=6:
            raise ValueError(
                f"Exactly 6 values required, you provided {len(values)}"
                )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True

def update_worksheet(data, worksheet):
    """
    Recieves a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided.
    """

    print (f"Updating {worksheet.capitalize()} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet.capitalize()} updated successfully.\n")


def calc_surplus_data(sales_row):

    """
    Compare sales with stock and calculate the surplus for each item type.

    The surplus is defined as the sales subtracted from the stock:
    = Positive surplus indicates wastes
    = Negative surplus indicates extra made when stock was sold out

    """

    print("Calculating surplus data...\n")
    stock = SHEET.worksheet("stock").get_all_values()
    stock_row = stock[-1]


    surplus_data = []
    for stock, sales in zip(stock_row, sales_row):
        surplus = int(stock) - sales
        surplus_data.append(surplus)
    
    return surplus_data

def get_last_sales():
    """
    Collects data from the previous 5 market days to calculate stock needed 
    and returns the data as a list of lists
    """

    sales = SHEET.worksheet("sales")
    
    columns = []

    for ind in range(1, 7):
        column = sales.col_values(ind)
        columns.append(column[-5:])
    return columns

def calc_stock_data(data):
    """
    calculate the avg
    """
    print("Calculating stock data...\n")

    new_stock_data = []

    for column in data:
        int_column = [int(num) for num in column]
        avg = sum(int_column) / len(int_column)
        stock_num = avg * 1.1
        new_stock_data.append(round(stock_num))

    return new_stock_data





def main():
    """
    Run all program functions
    """
    data = get_sales_data()
    sales_data = [int(num) for num in data]
    update_worksheet(sales_data, "sales")
    new_surplus_data = calc_surplus_data(sales_data)
    update_worksheet(new_surplus_data, "surplus")
    sales_columns = get_last_sales()
    stock_data = calc_stock_data(sales_columns)
    update_worksheet(stock_data, "stock")
    return stock_data


print("Welcome to Love Sandwiches Data Automation\n")
stock_data = main()

def get_stock_values(data):
    headings = SHEET.worksheet("surplus").row_values(1)


    print("Make the following number of sandwiches for next market\n")
    stock_dict = {headings[i] : data[i] for i in range(len(headings))}
    
    return stock_dict
    
stock_values = get_stock_values(stock_data)

print(stock_values)

