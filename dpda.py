import json
import tkinter as tk
from tkinter import filedialog, messagebox


class DPDA:
    def __init__(self, states, input_alphabet, stack_alphabet, in_transform, transitions,
                 initial_state, initial_stack_symbol, accepting_states):
        self._states = states  
        self._input_alphabet = input_alphabet 
        self._stack_alphabet = stack_alphabet  
        self._in_transform = in_transform  
        self._transitions = transitions  
        self._initial_state = initial_state
        self._initial_stack_symbol = initial_stack_symbol  
        self._accepting_states = accepting_states  
        self.history = []  
        self.output_string = ""  
        self.reset()  

    def reset(self):
        self._current_state = self._initial_state 
        self._stack = [self._initial_stack_symbol]  
        self.history.clear()  
        self.output_string = "" 
        self.history.append(f"Начальное состояние: {self._current_state}, стек: {self._initial_stack_symbol}")

    def accept(self, input_string):
        self.reset() 
        for symbol in input_string:
            result = self.step(symbol) 
            if not result[0]: 
                return result
        
        result = self.step("")  
        if not result[0]: 
            return result
        
        if self._current_state in self._accepting_states: 
            return (True, "")  
        
        return (False, "Цепочка не завершилась в принимающем состоянии")  

    def step(self, symbol):
        if symbol not in self._input_alphabet and symbol != "":
            return (False, f"В цепочке присутствуют посторонние символы (символа \"{symbol}\" нет в алфавите)!")

        stack_top = self._stack[-1] if self._stack else None  
        transition_key = f"({self._current_state}, {symbol}, {stack_top})" 

        if transition_key not in self._transitions:
            return (False, f"Нет перехода для ({self._current_state}, {symbol}, {stack_top})") 

        transition = self._transitions[transition_key]  
        next_state = transition[0]  
        new_stack_symbols = transition[1]  
        output_symbol = transition[2] if len(transition) > 2 else "" 

        for c in output_symbol:
            if c not in self._in_transform:
                return (False, f"Посторонний символ '{c}' в выходной цепочке!")  

        self._current_state = next_state  
        self._stack.pop()  

        for new_stack_symbol in reversed(new_stack_symbols):  
            self._stack.append(new_stack_symbol)  

        self.output_string += output_symbol  
        self.history.append(f"Текущее состояние: {self._current_state}, символ: {symbol}, "
                            f"стек: {', '.join(self._stack)}, выход: {self.output_string}")  

        return (True, "")  


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DPDA Automaton")
        self.geometry("600x400")
        self.dpda = None

        self.history_text = tk.Text(self, wrap=tk.WORD, height=10, width=50)
        self.history_text.pack(pady=10)

        self.input_label = tk.Label(self, text="Введите строку:")
        self.input_label.pack()

        self.input_text = tk.Entry(self)
        self.input_text.pack(pady=5)

        self.load_button = tk.Button(self, text="Загрузить автомат", command=self.load_automaton)
        self.load_button.pack(pady=5)

        self.check_button = tk.Button(self, text="Проверить строку", command=self.check_string)
        self.check_button.pack(pady=5)

    def load_automaton(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath:
            return
        try:
            self.dpda = self.load_automaton_from_file(filepath)
            messagebox.showinfo("Успех", "Автомат загружен успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки автомата: {str(e)}")

    def load_automaton_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return DPDA(
            data['states'],
            data['input_alphabet'],
            data['stack_alphabet'],
            data['in_transform'],
            data['transitions'],
            data['initial_state'],
            data['initial_stack_symbol'],
            data['accepting_states']
        )

    def check_string(self):
        if not self.dpda:
            messagebox.showerror("Ошибка", "Сначала загрузите автомат!")
            return

        input_string = self.input_text.get()
        result = self.dpda.accept(input_string)

        if result[0]:
            message = f"Цепочка принята\nИстория работы автомата:\n{chr(10).join(self.dpda.history)}\n"
            messagebox.showinfo("Выходная цепочка", self.dpda.output_string)
        else:
            message = f"Цепочка отклонена: {result[1]}\nИстория работы автомата:\n{chr(10).join(self.dpda.history)}"
        
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, message)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
