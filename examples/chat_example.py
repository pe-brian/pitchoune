from pitchoune.decorators import read_stream, write_stream, use_chat


with open("data/dummy.jsonl", "w") as file:
    file.write('{"id": 1, "a": 1, "b": 1}\n')
    file.write('{"id": 2, "a": 2, "b": 2}\n')
    file.write('{"id": 3, "a": 3, "b": 3}\n')
    file.write('{"id": 4, "a": 4, "b": 4}\n')
    file.write('{"id": 5, "a": 5, "b": 5}\n')
    file.write('{"id": 6, "a": 6, "b": 6}\n')


def validate_response(foo):
    """Validate the response from the chat model."""
    for _ in range(3):  # try 3 times
        res = foo()  # call the function
        try:
            return int(res)  # try to convert to int
        except ValueError as e:
            pass


@use_chat(name="multiply_agent", prompt="Complete the formula. Return only digits.", local=True, model="mistral-nemo")
@read_stream("data/dummy.jsonl", recover_progress_from="data/output.jsonl")
@write_stream("data/output.jsonl")
def main(id, a, b, multiply_agent):
    res = validate_response(lambda: multiply_agent.send_msg(f"{a}x{b}="))
    return {"id": id, "a": a, "b": b, "result": res}


if __name__ == "__main__":
    main()
 