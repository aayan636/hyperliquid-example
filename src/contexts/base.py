from abc import abstractmethod


class Context:

    @abstractmethod
    def fetch_data(self, *args, **kwargs) -> None:
        # Fetch data and store in object
        pass

    @abstractmethod
    def context_for_llm(self, *args, **kwargs) -> str:
        # Generate a string which will be entered into the LLM
        pass