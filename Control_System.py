#control_system.py
import subprocess 
from public_variable import FunFileL
from sql_record import registeruser
'''
"1. Scan your face for registration" 
"2. Train the model (You must finish 1 first!)
"3. Scan your face to enter" 
"4. Delete user information"
"5. Update users information"
'''
FuncList = ['1','2','3','4','5','6','7','8'] # a list for storing functions' number
#FunFileL = [
    #"/Users/alex_wcc/PycharmProjects/PythonProject/capture.py",
    #"/Users/alex_wcc/PycharmProjects/PythonProject/process_and_train.py",
    #"/Users/alex_wcc/PycharmProjects/PythonProject/track_and_recognize.py",
    #"/Users/alex_wcc/PycharmProjects/PythonProject/delete_user.py"
#]

while True:
    UserName = None
    print("Functions List\n1. Scan your face for registration. \
    \n2. Train the model (You must finish 1 first!). \
    \n3. Scan your face to enter. \
    \n4. Delete user information. \
    \n5. Update user information. \
    \n6. Generate residents' report. \
    \n7. Generate rooms' report. \
    \n8. Find the issue rooms\
    \nType 'END' or 'end' to stop the program.")
    
    Users_Option = str(input("Please choose the action: "))
    
    if Users_Option in FuncList:  # check the input
        print("\nValid input.\n")
        Users_Option = int(Users_Option)
        
        if Users_Option == 1:  # capture face
            UserName = str(input("Please enter your name: "))
            registeruser(UserName)
            subprocess.run(["python", FunFileL[Users_Option-1], "--name", UserName, "--num", "30", "--cam", "http://192.168.5.1:81/stream"]) #default cam = 0 for nonlocal camera
        
        elif Users_Option == 2:  # train model
            subprocess.run(["python", FunFileL[Users_Option-1]])
        
        elif Users_Option == 3:  # recognize user
            subprocess.run(["python", FunFileL[Users_Option-1]])
        
        elif Users_Option == 4:  # delete user
            UserName = str(input("Please enter the name for delete: "))
            subprocess.run(["python", FunFileL[Users_Option-1], "--name", UserName])
        
        elif Users_Option == 5:  # update user info
            UserName = str(input("Please enter the name for update: "))
            subprocess.run(["python", FunFileL[3], "--name", UserName])
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \
                  \nThe current data of {UserName} has been deleted.\
                    \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            subprocess.run(["python", FunFileL[0], "--name", UserName, "--num", "30", "--cam", "http://192.168.5.1:81/stream"])
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \
                  \nThe scanning part is finished.\
                    \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            subprocess.run(["python", FunFileL[1]])
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \
                  \nThe training part is finished.\
                    \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        elif Users_Option == 6:  # Generate residents' report.
            subprocess.run(["python", FunFileL[4]])
        elif Users_Option == 7:  # Generate residents' report.
            subprocess.run(["python", FunFileL[5]])
        elif Users_Option == 8:  # Generate residents' report.
            subprocess.run(["python", FunFileL[6]])
    elif Users_Option.lower() == "end":  # end the loop
        print("\nThe program is ended now.\n")
        break
    
    else:
        print("\nInvalid input, please enter again.\n")
