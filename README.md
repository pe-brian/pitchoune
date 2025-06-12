# Pitchoune

A Python library on top of Polars to load & save (normal or streaming mode) data from files & chat with LLM.

# Features

- Load / save dataframe :
    - Handle files types : xlsx, csv, tsv, jsonl
    - Possibility to register your own file types (see custom_io_example)

- Read / write stream :
    - Handle files types : jsonl (soon csv/tsv)
    - Call the decorated function for each row of the streamed file
    - Inject each column as a parameter of the function
    - Provide as parameters the current_row and total_row
    - Can handle recovery (in case of error or process stopping) with the parameter "recover_from".
      Just set it to the output file path and it will use the right row for the read_stream function.

- Current workdir for filepaths : set PITCHOUNE_WORKDIR env variable

- Save to a file with human check option enabled :
    - Open the file with the default editor
    - Then wait for the user to review it & save it

- Use chat :
    - Ollama chat (see chat_example)
    - OpenAI chat (you must then set OPENAI_API_KEY env variable)

# Todo

- Testing
