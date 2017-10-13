from sys import argv

# to do - fix it so that tag start mismatches work

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

    index_file_1 = 0
    index_file_2 = 0
    mismatches = False

    while len(file_1_stripped) > 0:
        index_file_1 += 1
        index_file_2 += 1
        if len(file_2_stripped) == 0:
            print("Unexpected end of file 2... aborting operation.")
            return 2
        elif file_1_stripped[0] != file_2_stripped[0]:
            mismatches = True
            # find_and_report_errors will find the errors
            continue_points = find_and_report_errors(file_1_stripped_copy, file_1_stripped, file_1_line_preserved, index_file_1,
                                                     file_2_stripped_copy, file_2_stripped, file_2_line_preserved, index_file_2)
            if type(continue_points) == bool and not continue_points:
                return 2
            else:
                file_1_stripped = file_1_stripped[continue_points[0]:]
                index_file_1 += continue_points[0]
                file_2_stripped = file_2_stripped[continue_points[1]:]
                index_file_2 += continue_points[1]
        file_1_stripped = file_1_stripped[1:]
        file_2_stripped = file_2_stripped[1:]
    if len(file_2_stripped) > 0:
        print("Unexpected end of file 1... aborting operation.")
        return 2

    return 1 if mismatches else 0


def find_and_report_errors(file_1_full: str, file_1_shortened: str, file_1_lines: str, file_1_error_start_index: int, file_2_full: str,
                           file_2_shortened: str, file_2_lines: str, file_2_error_start_index: int):
    # the eventual return if find_and_report completes; lets the function that calls it know what to remove.
    index_return = []

    if in_tag(file_1_shortened) or in_tag(file_2_shortened):
        tag_mismatch = get_tag_mismatch(file_1_full, file_1_shortened, file_1_error_start_index, file_2_full,
                                        file_2_shortened, file_2_error_start_index)
        # need to get start tag
        print("On the following lines...\nfile 1: #. " + tag_mismatch[2] + "\nfile 2: #. " + tag_mismatch[3] + "\n" +
              tag_mismatch[2] + " != " + tag_mismatch[3] + ". Tag mismatch. Attempting to continue to end of " +
              str(tag_mismatch[0]) + ". Succeeded.\n")

    # gets the nearest start tags for both files
    file_1_start_tag = find_previous_open_tag(file_1_full, file_1_error_start_index)
    file_2_start_tag = find_previous_open_tag(file_2_full, file_2_error_start_index)

    # gets the end tag that matches the start tag for both files
    file_1_end_tag = find_matching_close_tag(file_1_full, file_1_error_start_index, file_1_start_tag[0])
    file_2_end_tag = find_matching_close_tag(file_2_full, file_2_error_start_index, file_2_start_tag[0])

    # if there is no end tag in either file that can be found, stop searching and fail
    if file_1_end_tag[1] == -1 or file_2_end_tag[1] == -1:
        # returns true because the diff cannot continue.
        print("Closing tag seek failed... aborting operation.")
        return False

    # gets the string that contained an error (including parent tag)
    file_1_string_to_compare = file_1_full[file_1_start_tag[1]: file_1_end_tag[2]]

    # find the compare string's location in file_1's shortened string
    for index in range(0, len(file_1_string_to_compare)):
        if file_1_string_to_compare[index:] not in file_1_shortened:
            index_return.append(file_1_shortened.find(file_1_string_to_compare[index-1:]) +
                                len(file_1_string_to_compare[index-1:]))
            # no need to waste time, we've gotten our answer
            break

    # strips the outermost tags of the file 1 string to compare (we don't need it, we already know they match)
    file_1_string_to_compare = file_1_string_to_compare[file_1_string_to_compare.find('>') + 1: file_1_string_to_compare.rfind('<')]

    # same as above but for the second file
    file_2_string_to_compare = file_2_full[file_2_start_tag[1]: file_2_end_tag[2]]

    # perform the same as above for file_2
    for index in range(0, len(file_2_string_to_compare)):
        print(file_2_string_to_compare[index:])
        if file_2_string_to_compare[index:] not in file_2_shortened:
            index_return.append(file_2_shortened.find(file_2_string_to_compare[index-1:]) +
                                len(file_2_string_to_compare[index-1:]))

            # no need to waste time, we've gotten our answer
            break

    # strip the outermost tags of the file 2 string to compare (we don't need it, we already know they match)
    file_2_string_to_compare = file_2_string_to_compare[file_2_string_to_compare.find('>') + 1:file_2_string_to_compare.rfind('<')]

    file_1_string_currently_comparing = ""
    file_2_string_currently_comparing = ""

    while True:
        if len(file_1_string_to_compare) == 0 or len(file_2_string_to_compare) == 0:
            break
        # need to make a function out of this
        # builds the string until the next tag is found (for text mismatch)
        file_1_string_currently_comparing += build_string_until_tag(file_1_string_to_compare)
        file_1_string_to_compare = file_1_string_to_compare[len(file_1_string_currently_comparing):]

        file_2_string_currently_comparing += build_string_until_tag(file_2_string_to_compare)
        file_2_string_to_compare = file_2_string_to_compare[len(file_2_string_currently_comparing):]

        if file_1_string_currently_comparing != file_2_string_currently_comparing:
            if "<" not in file_1_string_currently_comparing:
                # have to get the lines here
                print("On the following lines...\nfile 1: #. " + file_1_full[file_1_start_tag[1]: file_1_end_tag[2]]
                      + "\nfile 2: #. " + file_2_full[file_2_start_tag[1]: file_2_end_tag[2]] + "\n\"" +
                      file_1_string_currently_comparing + "\" != \"" + file_2_string_currently_comparing +
                      "\". Simple text mismatch. Continuing.\n")

                if len(file_1_string_to_compare) == 0 or len(file_2_string_to_compare) == 0:
                    break

                file_1_string_currently_comparing = file_1_string_to_compare[0]
                file_2_string_currently_comparing = file_2_string_to_compare[0]

                file_1_string_to_compare = file_1_string_to_compare[1:]
                file_2_string_to_compare = file_2_string_to_compare[1:]

            else:
                # else its a tag, compare their innards to make sure they match, otherwise break the compare and
                # alert that there was a tag mismatch
                print("On the following lines...\nfile 1: #. " + file_1_full[file_1_start_tag[1]: file_1_end_tag[2]]
                      + "\nfile 2: #. " + file_2_full[file_2_start_tag[1]: file_2_end_tag[2]] + "\n" +
                      file_1_string_currently_comparing + " != " + file_2_string_currently_comparing +
                      ". Tag mismatch. Attempting to continue to end of " + file_1_start_tag[0] + ". Succeeded.\n")
                return index_return

    return index_return


def in_tag(shortened_string: str)->bool:
    if shortened_string.find(">") < shortened_string.find('<') or ('<' not in shortened_string and '>' in shortened_string):
        return True
    return False


def get_tag_mismatch(file_1_full: str, file_1_shortened: str, file_1_error_start_index: int, file_2_full: str,
                     file_2_shortened: str, file_2_error_start_index: int)->list:
    tag_mismatch = []
    file_1_shortened_opposite = file_1_full[:file_1_error_start_index + file_1_shortened.find('>')]
    file_2_shortened_opposite = file_2_full[:file_2_error_start_index + file_2_shortened.find('>')]

    file_1_tag = file_1_shortened_opposite[file_1_shortened_opposite.rfind('<'):]
    file_2_tag = file_2_shortened_opposite[file_2_shortened_opposite.rfind('<'):]

    tag_mismatch.append(len(file_1_shortened_opposite))
    tag_mismatch.append(len(file_2_shortened_opposite))
    tag_mismatch.append(file_1_tag)
    tag_mismatch.append(file_2_tag)

    return tag_mismatch
    # returns a list of where to continue off


def build_string_until_tag(full_string):
    built_string = ""
    while len(full_string) > 0 and full_string[0] != "<":
        built_string += full_string[0]
        full_string = full_string[1:]
    return built_string


def find_previous_open_tag(file_string: str, start_search_index: int)->list:
    string_copy = file_string[:start_search_index]
    if string_copy[-1] == '<':
        string_copy = string_copy[:-1]
    elif string_copy[-1] == '>':
        string_copy += file_string[:start_search_index+1]

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
    string_copy = file_string[start_search_index-1:]
    final_start_index = start_search_index-1
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
