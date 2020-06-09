class Colors:
    HEADER = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(Colors.BOLD + "=" * 46 + Colors.ENDC)
print(f"""{Colors.BOLD}      _____                   _ _      
     (____ \   /\            | (_)_    
      _   \ \ /  \  _   _  _ | |_| |_  
     | |   | / /\ \| | | |/ || | |  _) 
     | |__/ / |__| | |_| ( (_| | | |__ 
     |_____/|______|\____|\____|_|\___){Colors.ENDC}
      https://github.com/shouc/daudit""")
print(Colors.BOLD + "=" * 46 + Colors.ENDC)
print()
INFO = lambda x: print(f"{Colors.BOLD}{Colors.HEADER}[INFO]    {x}{Colors.ENDC}{Colors.ENDC}")
DEBUG = lambda x: print(f"{Colors.BOLD}{Colors.GREEN}[DEBUG]{Colors.ENDC}{Colors.ENDC}   {x}")
ERROR = lambda x: print(f"{Colors.BOLD}{Colors.RED}[ERROR]{Colors.ENDC}{Colors.ENDC}   {x}")
WARN = lambda x: print(f"{Colors.BOLD}{Colors.YELLOW}[WARNING]{Colors.ENDC}{Colors.ENDC} {x}")
RECOMMENDATION = lambda x: print(f"{Colors.BOLD}{Colors.GREEN}[RECOMM]{Colors.ENDC}{Colors.ENDC}  "
                                       f"Consider setting {x} in configuration file(s) based on your context.")
ISSUE = lambda x: print(f"{Colors.BOLD}{Colors.YELLOW}[ISSUE]{Colors.ENDC}{Colors.ENDC}   {x}")

