class PrintUtils:

    def p_green(self, text):
        print("\033[92m {}\033[00m" .format(text))

    def p_red(self, text):
        print("\033[91m {}\033[00m" .format(text))

    def p_yellow(self, text):
        print("\033[93m {}\033[00m" .format(text))

    def p_blue(self, text):
        print("\033[94m {}\033[00m" .format(text))

    def p_purple(self, text):
        print("\033[95m {}\033[00m" .format(text))

    def p_gray(self, text):
        print("\033[90m {}\033[00m" .format(text))

    def contprint(self, text):
        print(f"\033[96m {text}\033[00m...\t", end="")


    def p_warning(self, text: str):
        print("\n\n============================\n\n\033[93m {}\033[00m\n\n============================\n\n" .format(text.upper()))