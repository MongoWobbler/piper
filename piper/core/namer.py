#  Copyright (c) Christian Corsica. All Rights Reserved.

import re
import piper.config as pcfg


def removePrefixes(word, prefixes):
    """
    Attempts to remove the given prefixes from the given word.

    Args:
        word (string): Word to remove prefixes from.

        prefixes (collections.Iterable or string): Prefixes to remove from given word.

    Returns:
        (string): Word with prefixes removed.
    """
    if isinstance(prefixes, str):
        return word.split(prefixes)[-1]

    for prefix in prefixes:
        word = word.split(prefix)[-1]

    return word


def removeSuffixes(word, suffixes):
    """
    Attempts to remove the given suffixes from the given word.

    Args:
        word (string): Word to remove suffixes from.

        suffixes (collections.Iterable or string): Suffixes to remove from given word.

    Returns:
        (string): Word with suffixes removed.
    """
    if isinstance(suffixes, str):
        return word.split(suffixes)[0]

    for suffix in suffixes:
        word = word.split(suffix)[0]

    return word


def toSentenceCase(text):
    """
    Converts the given text to sentence case.

    Args:
        text (string): Text to convert to sentence case.

    Returns:
        (string): Sentence case version of given text.
    """
    return re.sub(r"(?<=\w)([A-Z])", r" \1", text).title()


def swapText(text, first=pcfg.left_suffix, second=pcfg.right_suffix):
    """
    Swaps the given first and seconds strings with each other in the given text.

    Args:
        text (string): Text to look for given first and second string to swap with each other.

        first (string): Text to swap with the second string.

        second (string): Text to swap with the first string.

    Returns:
        (string): Text with strings swapped if they were found. Else same text as before.
    """
    return re.sub(r'{a}|{b}'.format(a=first, b=second), lambda w: first if w.group() == second else second, text)
