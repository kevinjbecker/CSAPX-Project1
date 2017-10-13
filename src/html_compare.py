from sys import argv


def main():
    # to add: prompt for file names if argv no have them
    file_path_1 = argv[1]
    file_path_2 = argv[2]
    exit_codes = ["Files match.", "Files partially match with above differences.", "Files do not match."]

    # if the files are the same path, it is impossible for them to be different.
    # saving compute time by catching this case.
    if file_path_1 == file_path_2:
        print("Files point to same directory. Files match.")
    else:
        file_1_html = read_html_file(file_path_1)
        file_2_html = read_html_file(file_path_2)

        # again saving compute time
        if file_1_html == file_2_html:
            print("Files match.")
        else:
            file_1_stripped = strip_new_lines(file_1_html)
            file_1_line_preserved = replace_new_lines(file_1_html)
            file_2_stripped = strip_new_lines(file_2_html)
            file_2_line_preserved = replace_new_lines(file_2_html)

            # EXIT CODE KEY: 0 = MATCH, 1 = PARTIAL MATCH, 2 = NO MATCH
            exit_code = compare_files(file_1_stripped, file_1_line_preserved, file_2_stripped, file_2_line_preserved)

            print(exit_codes[exit_code])


def compare_files(file_1_stripped: str, file_1_line_preserved: str, file_2_stripped: str, file_2_line_preserved: str)->int:
    if file_1_stripped == file_2_stripped:
        return 0

    file_1_stripped_copy = file_1_stripped
    file_2_stripped_copy = file_2_stripped

    index = 0
    while len(file_1_stripped) > 0:
        index += 1
        if len(file_2_stripped) == 0:
            print("Unexpected end of file 2... aborting operation.\nFiles do not match.")
            break
        if file_1_stripped[0] != file_2_stripped[0]:
            continue_points = find_errors(file_1_stripped_copy, file_2_stripped_copy, file_1_line_preserved,
                                          file_2_line_preserved, index)
    return 0


def find_errors(file_1: str, file_2: str, file_1_lines: str, file_2_lines: str, start_index: int)->bool:

    # gets the nearest start tags for both files
    file_1_start_tag = find_previous_open_tag(file_1, start_index)
    file_2_start_tag = find_previous_open_tag(file_2, start_index)

    # gets the nearest end tags for both files
    file_1_end_tag = find_matching_close_tag(file_1, start_index, file_1_start_tag[0])
    file_2_end_tag = find_matching_close_tag(file_2, start_index, file_2_start_tag[0])

    # if there is no end tag in either file that can be found, stop searching and fail
    if file_1_end_tag[1] == -1 or file_2_end_tag[1] == -1:
        # returns true because the diff cannot continue.
        print("Closing tag seek failed... aborting operation.\nFiles do not match.")
        return True

    # used for text-mismatch
    file_1_compare_string = file_1[file_1_start_tag[1]: file_1_end_tag[2]]
    file_1_compare_string = file_1_compare_string[file_1_compare_string.find('>') + 1:]
    file_1_compare_string = file_1_compare_string[:file_1_compare_string.find('<')]

    file_2_compare_string = file_2[file_2_start_tag[1]: file_2_end_tag[2]]
    file_2_compare_string = file_2_compare_string[file_2_compare_string.find('>') + 1:]
    file_2_compare_string = file_2_compare_string[:file_2_compare_string.find('<')]

# still need to calculate number
    if file_1_compare_string != file_2_compare_string:
        print("On the following lines...\nfile 1: #. " + file_1[file_1_start_tag[1]: file_1_end_tag[2]]
              + "\nfile 2: #. " + file_2[file_2_start_tag[1]: file_2_end_tag[2]] + "\n\"" +
              file_1_compare_string+"\" != \"" + file_2_compare_string +
              "\". Simple text mismatch. Continuing.")


def find_previous_open_tag(file_string: str, start_search_index: int)->list:
    string_copy = file_string[:start_search_index]

    current_tag_start_index = string_copy.rfind("<")
    current_tag_end_index = string_copy.rfind(">")

    while True:
        tag = file_string[current_tag_start_index: current_tag_end_index+1]

        if "/" not in tag:
            return [tag, current_tag_start_index, current_tag_end_index+1]
        else:
            string_copy = string_copy[:current_tag_start_index]
            current_tag_start_index = string_copy.rfind("<")
            current_tag_end_index = string_copy.rfind(">")


def find_matching_close_tag(file_string: str, start_search_index: int, tag_to_match: str)->list:
    string_copy = file_string[start_search_index:]
    final_start_index = start_search_index
    close_tags_remaining = 1

    current_tag_start_index = string_copy.find("<")
    final_start_index += current_tag_start_index

    current_tag_end_index = string_copy.find(">")

    while True:
        if current_tag_end_index == -1:
            return ["", -1, -1]

        tag = string_copy[current_tag_start_index: current_tag_end_index+1]
        final_start_index += len(tag)

        if tag == tag_to_match:
            close_tags_remaining += 1
        elif tag.replace('/', '') == tag_to_match:
            close_tags_remaining -= 1
            if close_tags_remaining == 0:
                final_start_index -= len(tag)
                return [tag, final_start_index, final_start_index + (current_tag_end_index - current_tag_start_index) + 1]
        else:
            string_copy = string_copy[current_tag_end_index + 1:]
            current_tag_start_index = string_copy.find("<")
            current_tag_end_index = string_copy.find(">")


def read_html_file(html_file_path: str)->str:
    html_file_string = ""
    with open(html_file_path) as file:
        for line in file:
            html_file_string += line
    return html_file_string


def strip_white_space(html_string: str, new_lines: bool = False)->str:
    to_return = " ".join(html_string.split()).replace("> <", "><").replace("> ", ">").replace(" <", "<")
    if new_lines:
        to_return = to_return.replace(">$ ", ">")
    return to_return


def strip_new_lines(html_string: str)->str:
    return strip_white_space(html_string.replace('\n', ''))


def replace_new_lines(html_string: str)->str:
    return strip_white_space(html_string.replace('\n', '$'), True)


if __name__ == '__main__':
    main()
