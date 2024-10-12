from dataclasses import dataclass
from typing import List, Union, TypeAlias

HTree: TypeAlias = Union[None, 'HuffmanNode']

@dataclass
class HuffmanNode:
    char_ascii: int         # stored as an integer - the ASCII character code value
    freq: int               # the frequency associated with the node
    left: HTree = None      # Huffman tree (node) to the left
    right: HTree = None     # Huffman tree (node) to the right

    def __lt__(self, other: 'HuffmanNode') -> bool:
        return comes_before(self, other)


def comes_before(a: HuffmanNode, b: HuffmanNode) -> bool:
    """Returns True if tree rooted at node a comes before tree rooted at node b, False otherwise"""
    if a.freq > b.freq:
        return False
    elif a.freq < b.freq:
        return True
    elif a.freq == b.freq:
        if a.char_ascii < b.char_ascii:
            return True
        else:
            return False


def combine(a: HuffmanNode, b: HuffmanNode) -> HuffmanNode:
    """Creates a new Huffman node with children a and b, with the "lesser node" on the left
    The new node's frequency value will be the sum of the a and b frequencies
    The new node's char value will be the lower of the a and b char ASCII values"""
    new_node = HuffmanNode(0, 0, None, None)
    new_node.freq = a.freq + b.freq
    new_node.char_ascii = min(a.char_ascii, b.char_ascii)
    if a < b:
        new_node.left = a
        new_node.right = b
    else:
        new_node.left = b
        new_node.right = a
    return new_node


def cnt_freq(filename: str) -> List:
    """Opens a text file with a given file name (passed as a string) and counts the
    frequency of occurrences of all the characters within that file
    Returns a Python List with 256 entries - counts are initialized to zero.
    The ASCII value of the characters are used to index into this list for the frequency counts"""
    ret_list = [0]*256
    with open(filename, "r") as in_file:
        for line in in_file:
            for i in line:
                asc = ord(i)
                ret_list[asc] += 1
    return ret_list


def create_huff_tree(char_freq: List) -> HTree:
    """Input is the list of frequencies (provided by cnt_freq()).
    Create a Huffman tree for characters with non-zero frequency
    Returns the root node of the Huffman tree. Returns None if all counts are zero."""
    huff_list = []
    for i in range(len(char_freq)):
        if char_freq[i] != 0:
            huff_list.append(HuffmanNode(i, char_freq[i]))

    if len(huff_list) == 0:
        return None

    if len(huff_list) == 1:
        return huff_list[0]

    huff_list.sort()

    while len(huff_list) > 1:
        comb = combine(huff_list[0], huff_list[1])
        huff_list.append(comb)
        del(huff_list[0])
        del(huff_list[0])
        huff_list.sort()

    return huff_list[0]


def create_code(node: HTree) -> List:
    """Returns an array (Python list) of Huffman codes. For each character, use the integer ASCII representation
    as the index into the array, with the resulting Huffman code for that character stored at that location.
    Characters that are unused should have an empty string at that location"""
    ret_list = [""]*256
    cur_str = ""
    if node is None:
        return []
    create_code_helper(node, cur_str, ret_list)
    return ret_list

def create_code_helper(node: HTree, cur_str: str, ret_list: List) -> None:
    if node.left is not None:
        cur_str += "0"
        create_code_helper(node.left, cur_str, ret_list)
        cur_str = cur_str[:-1]
    if node.right is not None:
        cur_str += "1"
        create_code_helper(node.right, cur_str, ret_list)
        cur_str = cur_str[:-1]
    if node.right is None and node.left is None:
        ret_list[node.char_ascii] = cur_str


def create_header(freqs: List) -> str:
    """Input is the list of frequencies (provided by cnt_freq()).
    Creates and returns a header for the output file
    Example: For the frequency list asscoaied with "aaabbbbcc, would return “97 3 98 4 99 2” """
    str_list = []
    for i in range(len(freqs)):
        if freqs[i] != 0:
            str_list.append(i)
            str_list.append(freqs[i])
    ret_str = " ".join(str(i) for i in str_list)
    return ret_str


def huffman_encode(in_file: str, out_file: str) -> None:
    """Takes inout file name and output file name as parameters
    Uses the Huffman coding process on the text from the input file and writes encoded text to output file
    Take not of special cases - empty file and file with only one unique character"""
    code_list = []
    with open(in_file, "r") as inpt:
        for line in inpt:
            for i in line:
                code_list.append(i)
    count = cnt_freq(in_file)
    head = create_header(count)
    h_tree = create_huff_tree(count)
    code = create_code(h_tree)
    with open(out_file, "w", newline='') as output:
        output.write(head + "\n")
        for i in code_list:
            output.write(code[ord(i)])





###
#               PART B
###


def huffman_decode(encoded_file, decode_file) -> None:
    try:
        with open(encoded_file) as in_file:
            first_line = in_file.readline()
            freqs = parse_header(first_line)
            huff_tree = create_huff_tree(freqs)
            encode = in_file.readline()
            out_text = []
            huffman_decode_helper(encode, out_text, huff_tree, huff_tree)
            ret_str = "".join(out_text)

        with open(decode_file, "w") as out_file:
            out_file.write(ret_str)
    except FileNotFoundError:
        raise FileNotFoundError


def huffman_decode_helper(encode, out_text, position, root) -> str:
    if position.left is None and position.right is None:                #this is a leaf node
        char = str(chr(position.char_ascii))
        out_text += char
        if len(encode) > 0:
            position = root
            huffman_decode_helper(encode, out_text, position, root)
        else:
            return out_text


    else:                                                               #this is NOT a leaf node
        if encode[0] == "1":
            if position.right is not None:
                position = position.right
                encode = encode[1:]
                huffman_decode_helper(encode, out_text, position, root)
        elif encode[0] == "0":
            if position.left is not None:
                position = position.left
                encode = encode[1:]
                huffman_decode_helper(encode, out_text, position, root)



def parse_header(header_string) -> List:
    ret_list = [0] * 256
    header_list = header_string.split(" ")
    int_list = [eval(i) for i in header_list]
    for i in range(0, len(header_list), 2):
        ret_list[int_list[i]] = int_list[i + 1]

    return ret_list
