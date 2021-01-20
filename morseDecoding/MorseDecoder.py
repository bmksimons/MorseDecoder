from GPIOSimulator_v1 import *
import time

GPIO = GPIOSimulator()

MORSE_CODE = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
              '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
              '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
              '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y', '--..': 'z', '.----': '1',
              '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
              '---..': '8', '----.': '9', '-----': '0'}


class MorseDecoder():

    def __init__(self):
        self.current_symbol = ""
        self.current_word = ""
        self.T = 0.5
        self.result = ""
        GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(PIN_RED_LED_0, GPIO.OUT, GPIO.LOW)
        GPIO.setup(PIN_RED_LED_1, GPIO.OUT, GPIO.LOW)
        GPIO.setup(PIN_RED_LED_2, GPIO.OUT, GPIO.LOW)
        GPIO.setup(PIN_BLUE_LED, GPIO.OUT, GPIO.LOW)

    def decoding_loop(self):
        """ the main decoding loop """
        try:
            while True:
                self.read_one_signal()
        except KeyboardInterrupt:
            if self.current_symbol != "" or self.current_word != "":
                self.handle_word_end()
            print("The message was:" + self.result)

    def read_one_signal(self):
        """ uses evaluate_input to read a signal from GPIOSimulator and sends the results to process_signal"""
        if self.evaluate_input() == 1:  # is the signal a dot/dash?
            start = time.time()
            end = self.find_end_time(1)
            if end is not None:
                self.process_signal(end - start)
        elif self.evaluate_input() == 0 and self.current_symbol != "":  # is the signal a pause?
            start = time.time()
            end = self.find_end_time(0)
            if end is not None:
                self.process_signal(end - start)

    def find_end_time(self, GPIO_Pud):
        """ helper function used in read_one_signal to find the end time of the signal """
        helper_bool = self.evaluate_input() == GPIO_Pud
        while helper_bool:
            helper_bool = self.evaluate_input() == GPIO_Pud
        return time.time()

    def process_signal(self, signal):
        """ handle the signals using corresponding functions """
        if self.evaluate_input() == 0:  # was the signal a dot/dash?
            if signal > self.T:
                GPIO.output(PIN_RED_LED_0, GPIO.HIGH)
                GPIO.output(PIN_RED_LED_1, GPIO.HIGH)
                GPIO.output(PIN_RED_LED_2, GPIO.HIGH)
                self.update_current_symbol("-")
            else:
                GPIO.output(PIN_BLUE_LED, GPIO.HIGH)
                self.update_current_symbol(".")
        elif self.evaluate_input() == 1:  # was the signal a pause?
            if signal > 7 * self.T:  # is the signal the end of a word?
                self.handle_word_end()
            elif signal > 4 * self.T:  # is the signal the end of a symbol?
                self.handle_symbol_end()

    def evaluate_input(self):
        """ Helper function that fixes the mistakes the GPIO.input method can make """
        pin_input = 0
        for i in range(5):
            pin_input += GPIO.input(PIN_BTN)
        average = pin_input / 5
        return round(average)

    def update_current_symbol(self, signal):
        """ append the signal to current symbol code """
        self.current_symbol += signal
        self.set_leds_low()

    def set_leds_low(self):
        """ resets the LED outputs after a signal has been registered """
        GPIO.output(PIN_RED_LED_0, GPIO.LOW)
        GPIO.output(PIN_RED_LED_1, GPIO.LOW)
        GPIO.output(PIN_RED_LED_2, GPIO.LOW)
        GPIO.output(PIN_BLUE_LED, GPIO.LOW)

    def update_current_word(self, symbol):
        """ append the symbol to the current word """
        self.current_word += symbol

    def handle_symbol_end(self):
        """ process when a symbol ending appears """
        try:
            self.update_current_word(MORSE_CODE[self.current_symbol])
            self.current_symbol = ""
        except KeyError:
            print(self.current_symbol + " is invalid symbol in the morse code alphabet")
            self.current_symbol = ""

    def handle_word_end(self):
        """ process when a word ending appears """
        self.handle_symbol_end()
        self.result += " " + self.current_word
        self.current_word = ""


def main():
    mocoder = MorseDecoder()
    mocoder.decoding_loop()


if __name__ == "__main__":
    main()
