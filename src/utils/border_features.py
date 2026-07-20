def longest_border_length(token: str) -> int:
    max_length = 0
    for length in range(1, len(token)):
        if token[:length] == token[-length:]:
            max_length = length
    return max_length


def normalized_border_length(token: str) -> float:
    if len(token) <= 1:
        return 0.0
    return longest_border_length(token) / (len(token) - 1)
