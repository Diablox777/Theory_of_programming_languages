import json
import tkinter as tk
from tkinter import filedialog, messagebox


class DPDA:
    def __init__(self, states, input_alphabet, stack_alphabet, in_transform, transitions,
                 initial_state, initial_stack_symbol, accepting_states):
        # Инициализация параметров автомата
        self._states = states  # Множество состояний
        self._input_alphabet = input_alphabet  # Алфавит входных символов
        self._stack_alphabet = stack_alphabet  # Алфавит символов стека
        self._in_transform = in_transform  # Символы, которые могут быть в выходной цепочке
        self._transitions = transitions  # Переходы автомата
        self._initial_state = initial_state  # Начальное состояние
        self._initial_stack_symbol = initial_stack_symbol  # Начальный символ стека
        self._accepting_states = accepting_states  # Принимающие состояния
        self.history = []  # История работы автомата
        self.output_string = ""  # Выходная строка автомата
        self.reset()  # Сброс состояния автомата

    def reset(self):
        # Сброс состояния автомата до начального
        self._current_state = self._initial_state  # Установка текущего состояния в начальное
        self._stack = [self._initial_stack_symbol]  # Инициализация стека с начальным символом
        self.history.clear()  # Очистка истории работы
        self.output_string = ""  # Очистка выходной строки
        self.history.append(f"Начальное состояние: {self._current_state}, стек: {self._initial_stack_symbol}")

    def accept(self, input_string):
        # Метод для проверки принятия строки автоматом
        self.reset()  # Сброс состояния перед проверкой новой строки
        for symbol in input_string:
            result = self.step(symbol)  # Выполнение одного шага для каждого символа строки
            if not result[0]:  # Если шаг не удался, вернуть результат
                return result
        
        result = self.step("")  # Выполнение шага для пустого символа (завершение ввода)
        if not result[0]:  # Если шаг не удался, вернуть результат
            return result
        
        if self._current_state in self._accepting_states:  # Проверка на принимающее состояние
            return (True, "")  # Строка принята
        
        return (False, "Цепочка не завершилась в принимающем состоянии")  # Строка не принята

    def step(self, symbol):
        # Метод для выполнения одного шага автомата
        if symbol not in self._input_alphabet and symbol != "":
            return (False, f"В цепочке присутствуют посторонние символы (символа \"{symbol}\" нет в алфавите)!")

        stack_top = self._stack[-1] if self._stack else None  # Получаем верхний символ стека или None если стек пустой
        transition_key = f"({self._current_state}, {symbol}, {stack_top})"  # Формируем ключ для перехода

        if transition_key not in self._transitions:
            return (False, f"Нет перехода для ({self._current_state}, {symbol}, {stack_top})")  # Нет подходящего перехода

        transition = self._transitions[transition_key]  # Получаем переход по ключу
        next_state = transition[0]  # Следующее состояние из перехода
        new_stack_symbols = transition[1]  # Новые символы для стека из перехода
        output_symbol = transition[2] if len(transition) > 2 else ""  # Выходной символ

        for c in output_symbol:
            if c not in self._in_transform:
                return (False, f"Посторонний символ '{c}' в выходной цепочке!")  # Проверка на посторонние символы в выходе

        self._current_state = next_state  # Переход в следующее состояние
        self._stack.pop()  # Убираем верхний символ стека

        for new_stack_symbol in reversed(new_stack_symbols):  
            self._stack.append(new_stack_symbol)  # Добавляем новые символы в стек

        self.output_string += output_symbol  # Обновляем выходную строку
        self.history.append(f"Текущее состояние: {self._current_state}, символ: {symbol}, "
                            f"стек: {', '.join(self._stack)}, выход: {self.output_string}")  # Записываем историю работы

        return (True, "")  # Успешный шаг


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
