"""Oksana Dziuba"""

from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    next_states: list[State]

    @abstractmethod
    def __init__(self) -> None:
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occurred character is handled by current state
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string") 

class StartState(State):

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False # Implement


class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return True # Implement


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol # Implement

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym # Implement


class StarState(State):

    def __init__(self, checking_state: State):

        super().__init__()
        self.checking_state = checking_state
        checking_state.next_states.append(self)
        self.next_states = [checking_state] # Implement

    def check_self(self, char):
        return self.checking_state.check_self(char)



class PlusState(State):

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        checking_state.next_states.append(self)
        self.next_states = [checking_state] # Implement

    def check_self(self, char):
        return self.checking_state.check_self(char) # Implement


class RegexFSM:

    def __init__(self, regex_expr: str) -> None:
        self.entry  = StartState()
        self.exit = TerminationState()
        self.states = [self.entry]

        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]

            if char in "*+":
                raise ValueError(f"Regex cannot start with '{char}'")

            if char == "." or char.isascii() and char not in "*+":
                node = DotState() if char == "." else AsciiState(char)
                self.states[-1].next_states.append(node)
                self.states.append(node)
                i += 1

            if i < len(regex_expr) and regex_expr[i] in "*+":
                operator = regex_expr[i]
                prev = self.states.pop()
                wrapped = StarState(prev) if operator == "*" else PlusState(prev)

                for state in self.states[::-1]:
                    if prev in state.next_states:
                        state.next_states = [wrapped if s is prev else s for s in state.next_states]
                        break
                self.states.append(wrapped)
                i += 1

        self.states[-1].next_states.append(self.exit)


    def check_string(self, s: str) -> bool:
        def explore(state: State, pos: int) -> bool:
            if isinstance(state, TerminationState):
                return pos == len(s)

            accepted = False
            if pos < len(s) and state.check_self(s[pos]):
                for nxt in state.next_states:
                    if explore(nxt, pos + 1):
                        return True
                accepted = accepted or False


            if isinstance(state, (StarState, PlusState)):
                for nxt in state.next_states:
                    if explore(nxt, pos):
                        return True

            return accepted


        for first in self.entry.next_states:
            if explore(first, 0):
                return True
        return False # Implement

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False