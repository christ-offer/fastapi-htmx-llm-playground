import tiktoken

def num_tokens_from_messages(message, model):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows {role/name}\n{content}\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(message, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(message, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    if message.get("function_call"):
        num_tokens = len(encoding.encode(message.function_call.arguments))
    else:
        num_tokens = len(encoding.encode(message.content))
    num_tokens += 7  # every reply is primed with assistant
    return num_tokens


def calculate_cost(num_tokens, model="gpt-4-0613"):
    """Calculate the cost based on the number of tokens and the model."""
    if model is not None:
        if model == "gpt-3.5-turbo-0613":
            cost_per_token = 0.000002
        elif model == "gpt-3.5-turbo-16k-0613":
            cost_per_token = 0.000004
        elif model == "gpt-4-0314":
            cost_per_token = 0.00006
        elif model == "gpt-4-32k-0314":
            cost_per_token = 0.00012
        elif model == "gpt-4-0613":
            cost_per_token = 0.00006
        elif model == "gpt-4-32k-0613":
            cost_per_token = 0.00012
        elif model == "gpt-4":
            cost_per_token = 0.00012
        else:
            raise NotImplementedError(
                f"""calculate_cost() is not implemented for model {model}."""
            )
        cost = num_tokens * cost_per_token
    return cost
