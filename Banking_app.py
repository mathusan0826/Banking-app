import hashlib   # secure hashing and message digest algorithms. SHA-256 (sha256),MD5 (md5),SHA-1 (sha1),SHA-512 (sha512)
import os        #encode passwords securely
import datetime  # Importing datetime for timestamps

# -------------------- Utility Functions --------------------
def encode_password(password):
    return hashlib.sha256(password.encode()).hexdigest() #password encoding code

# -------------------- Global Data --------------------
ADMIN_USERNAME = "Admin"                       ## Admin default name
ADMIN_PASSWORD_HASH = encode_password("0826")  # Admin default password

user_credentials = {}  # {username: {"password": hash, "account_no": int}}
accounts = {}          # {account_no: {"name": str, "balance": float, "transactions": list}}

next_account_number = 1001  # next unique bank account

def generate_account_number():
    global next_account_number     #modifying the global variable
    acc_num = next_account_number  #Save the current account number
    next_account_number += 1       #Increment the global account number for the next user
    return acc_num                 #Return the current account number 

# -------------------- File Handling --------------------
def save_data():
    # Save user credentials
    with open("user.txt", "w") as f:
        for username, data in user_credentials.items():
            f.write(f"{username},{data['password']},{data['account_no']}\n")
    
    # Save accounts
    with open("customer.txt", "w") as f:
        for acc_no, data in accounts.items():
            f.write(f"{acc_no},{data['name']},{data['balance']}\n")
    
    # Save transactions
    with open("transaction.txt", "w") as f:
        for acc_no, data in accounts.items():
            for transaction in data["transactions"]:
                f.write(f"{acc_no},{transaction}\n")
    
    # Save bank accounts
    with open("bankaccount.txt", "w") as f:
        f.write(f"Next account number: {next_account_number}\n")
     

def load_data():
    global next_account_number  # To update the next_account_number properly
    if os.path.exists("user.txt"):
        with open("user.txt", "r") as f:
            for line in f:
                username, password, acc_no = line.strip().split(",")
                user_credentials[username] = {"password": password, "account_no": int(acc_no)}
    
    if os.path.exists("customer.txt"):
        with open("customer.txt", "r") as f:
            for line in f:
                acc_no, name, balance = line.strip().split(",")
                accounts[int(acc_no)] = {"name": name, "balance": float(balance), "transactions": []}
    
    if os.path.exists("transaction.txt"):
        with open("transaction.txt", "r") as f:
            for line in f:
                acc_no, transaction = line.strip().split(",", 1)
                if int(acc_no) in accounts:
                    accounts[int(acc_no)]["transactions"].append(transaction)
    
    if os.path.exists("bankaccount.txt"):
        with open("bankaccount.txt", "r") as f:
            next_account_number_line = f.readline()
            if next_account_number_line.startswith("Next account number:"):
                next_account_number = int(next_account_number_line.split(":")[1].strip())

#start
def load_user_credentials():
    credentials = {}
    try:
        with open("user.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    username, password, account_no = parts
                    credentials[username] = {
                        "password": password,
                        "account_no": account_no
                    }
    except FileNotFoundError:
        print("User file not found. Returning empty credentials.")
    return credentials

#end


# -------------------- Registration --------------------
def register_user():
    username = input(" Enter new username: ")
    if username in user_credentials:
        print(" Username already exists.")
        return

    password = input(" Enter new password: ")
    hashed_pw = encode_password(password)

    try:
        name = input(" Enter Account Holder Name: ")
        initial_balance = float(input(" Enter initial balance: "))
        if initial_balance < 0:
            print(" Initial balance cannot be negative.")
            return
    except ValueError:
        print(" Invalid balance amount.")
        return

    acc_no = generate_account_number()

    user_credentials[username] = {"password": hashed_pw, "account_no": acc_no}
    accounts[acc_no] = {
        "name": name,
        "balance": initial_balance,
        "transactions": [f"Initial deposit: Rs{initial_balance} on {datetime.datetime.now()}"]
    }

    print(f" Account created successfully! Account No: {acc_no}")
    save_data()

# -------------------- Login --------------------
def login():
    username = input(" User Name: ")
    password = input(" User Password: ")
    hashed = encode_password(password)
    load_user_credentials()

    if username == ADMIN_USERNAME and hashed == ADMIN_PASSWORD_HASH:
        print("🎈🎈🎈Admin login successful.🎈🎈🎈🎈")
        return "admin"
    elif username in user_credentials and user_credentials[username]["password"] == hashed:
        print(" User login successful.")
        return user_credentials[username]["account_no"]
    else:
        print(" Invalid Admin name or Password please chake.")
        return None

# -------------------- Banking Functions --------------------
def deposit(account_no):
    try:
        amount = float(input("Enter amount to deposit: "))
        if amount <= 0:
            print(" Must be a positive amount.")
            return
        accounts[account_no]["balance"] += amount
        accounts[account_no]["transactions"].append(f"Deposited: Rs{amount} on {datetime.datetime.now()}")
        print(" Deposit successful.")
        save_data()
    except ValueError:
        print(" Invalid input.")

def withdraw(account_no):
    try:
        amount = float(input(" Enter amount to withdraw: "))
        if amount <= 0:
            print(" Must be a positive amount.")
            return
        if accounts[account_no]["balance"] < amount:
            print(" Insufficient funds.")
            return
        accounts[account_no]["balance"] -= amount
        accounts[account_no]["transactions"].append(f"Withdrawn: Rs{amount} on {datetime.datetime.now()}")
        print("Withdrawal successful.")
        save_data()
    except ValueError:
        print(" Invalid input.")

def check_balance(account_no):
    print(f" Current Balance: Rs{accounts[account_no]['balance']}")

def view_transactions(account_no):
    print(" Transaction History:")
    for t in accounts[account_no]["transactions"]:
        print(" -", t)

# -------------------- Menus --------------------
def admin_menu():
    while True:
        print("\n🔐🔐🔏 Admin Menu🔑🔑🔑")
        print("1. View All Accounts 📂")
        print("2. Logout🔏")
        choice = input("Choose: ")
        if choice == "1":
            for acc_no, info in accounts.items():
                print(f"Account {acc_no}: {info['name']} - Rs{info['balance']}")
        elif choice == "2":
            break
        else:
            print(" Invalid choice.")

def user_menu(account_no):
    while True:
        print("\n User Menu")
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Check Balance")
        print("4. View Transaction History")
        print("5. Logout")
        choice = input("Choose: ")
        if choice == "1":
            deposit(account_no)
        elif choice == "2":
            withdraw(account_no)
        elif choice == "3":
            print("====================================")
            print("=Balance===========Amount===========")
            check_balance(account_no)
            print("====================================")
        elif choice == "4":
            print("==========================================================")
            print("=Transaction===Amount======Date======Time=================")
            view_transactions(account_no)
            print("==========================================================")
        elif choice == "5":
            break
        else:
            print(" Invalid choice.")

# -------------------- Main Program --------------------
def main():
    load_data()  # Load data at the start of the program
    while True:
        print("\n 😍😍😍 Welcome to Mini Bank 😍😍😍")
        print("1. Login 🔐")
        print("2. Register (User)  🤝")
        print("3. Exit 🖐")
        choice = input("Enter choice: ")
        if choice == "1":
            result = login()
            if result == "admin":
                admin_menu()
            elif isinstance(result, int):
                user_menu(result)
        elif choice == "2":
            register_user()
        elif choice == "3":
            print("👍👍👍 Thank you for using Mini Bank")
            save_data()
            break
        else:
            print("1 Invalid choice.")

# Run the application
main()